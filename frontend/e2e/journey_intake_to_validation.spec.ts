import { test, expect } from './_pipeline_guard';

/**
 * End-to-End Journey Test: Intake Submission → Validation
 * 
 * This test covers the complete user journey for the core disruption management workflow:
 * - Disruption Manager submits an inbox email
 * - System parses attachment into candidate rows
 * - Classification recommendation is generated
 * - System extracts VINs from parsed rows
 * - System validates VINs against BR-01 rules
 * - System records audit trail for all actions
 * 
 * Covers: FR-001, FR-002, FR-003, FR-004, FR-005
 * 
 * Note: This test uses Disruption Manager role throughout. BR-06 AMBER gate
 * enforcement for Event Approval Reviewer is tested separately in wireframe tests.
 */

test.describe('Journey: Intake to Validation', () => {
  let caseId: string;
  let attachmentId: string;
  let authToken: string;

  test('complete disruption workflow from intake to validation', async ({ page, request }) => {
    // ========================================
    // STEP 1: Login as Disruption Manager
    // ========================================
    await page.goto('/login');
    await page.fill('#email', 'disruption.mgr@tmna.com');
    await page.fill('#password', 'Manager123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
    
    // Extract auth token from localStorage for API calls
    authToken = await page.evaluate(() => localStorage.getItem('access_token') || '');
    expect(authToken).toBeTruthy();

    // ========================================
    // STEP 2: Submit Inbox Email (FR-001)
    // ========================================
    const submissionResponse = await request.post('/api/v1/intake/submissions', {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: {
        source_email_id: `e2e-test-${Date.now()}@disruptions.tmna.com`,
        source_address: 'e2e-supplier@supplier.com',
        received_at_utc: new Date().toISOString(),
        subject: 'E2E Test: Part Shortage - VIN List Attached',
        has_attachments: true,
      },
    });

    expect(submissionResponse.ok()).toBeTruthy();
    const submissionData = await submissionResponse.json();
    caseId = submissionData.id;
    expect(submissionData.case_key).toMatch(/^CASE-\d{8}-.{8}$/);
    expect(submissionData.intake_status).toBe('received');
    expect(submissionData.attachments).toHaveLength(1);
    attachmentId = submissionData.attachments[0].id;

    console.log(`Created case: ${submissionData.case_key} (${caseId})`);

    // Verify receipt metadata recorded (FR-001)
    expect(submissionData.source_email_id).toContain('e2e-test-');
    expect(submissionData.source_address).toBe('e2e-supplier@supplier.com');
    expect(submissionData.subject).toContain('E2E Test');
    expect(submissionData.received_at_utc).toBeTruthy();

    // ========================================
    // STEP 3: Parse Attachment (FR-002)
    // ========================================
    const parseResponse = await request.post(`/api/v1/parsing/attachments/${attachmentId}/parse`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: { force_reparse: false },
    });

    expect(parseResponse.ok()).toBeTruthy();
    const parseData = await parseResponse.json();
    expect(parseData.parse_status).toBe('parsed');
    expect(parseData.row_count).toBeGreaterThan(0);
    expect(parseData.lineage_base_ref).toContain('lin-');

    console.log(`Parsed ${parseData.row_count} candidate rows`);

    // Verify candidate rows created with lineage (FR-002)
    const rowsResponse = await request.get(`/api/v1/parsing/cases/${caseId}/rows`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
    });
    expect(rowsResponse.ok()).toBeTruthy();
    const rowsData = await rowsResponse.json();
    expect(Array.isArray(rowsData)).toBeTruthy();
    expect(rowsData.length).toBeGreaterThan(0);
    expect(rowsData[0].lineage_ref).toMatch(/^lin-.+\/att-.+\/r\d+$/);

    // ========================================
    // STEP 4: Generate Classification Recommendation (FR-003)
    // ========================================
    const recommendationResponse = await request.post(
      `/api/v1/classification/cases/${caseId}/recommendation`,
      {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
      }
    );

    expect(recommendationResponse.ok()).toBeTruthy();
    const recommendationData = await recommendationResponse.json();
    expect(recommendationData.suggested_disruption_type).toBeTruthy();
    expect(recommendationData.confidence_score).toBeGreaterThan(0);
    expect(recommendationData.confidence_score).toBeLessThanOrEqual(1);

    console.log(`Generated recommendation: ${recommendationData.suggested_disruption_type} (confidence: ${recommendationData.confidence_score})`);

    // Verify case status updated
    const caseAfterRecommendation = await request.get(`/api/v1/intake/cases/${caseId}`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
    });
    const caseAfterRecommendationData = await caseAfterRecommendation.json();
    expect(caseAfterRecommendationData.intake_status).toBe('classification_pending_review');

    // ========================================
    // STEP 5: Extract VINs (FR-004)
    // Note: Skipping classification decision step due to BR-06 role check
    // ========================================
    const extractionResponse = await request.post(`/api/v1/vins/cases/${caseId}/extract`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });

    expect(extractionResponse.ok()).toBeTruthy();
    const extractionData = await extractionResponse.json();
    expect(extractionData.extracted_count).toBeGreaterThan(0);
    expect(extractionData.run_status).toBe('completed');

    console.log(`Extracted ${extractionData.extracted_count} VINs (${extractionData.deduplicated_count} duplicates, ${extractionData.rejected_empty_count} rejected)`);

    // Verify VINs extracted and normalized (FR-004)
    expect(extractionData.extracted_count).toBeGreaterThanOrEqual(1);

    // ========================================
    // STEP 6: Validate VINs (FR-005)
    // ========================================
    const validationResponse = await request.post(`/api/v1/vins/cases/${caseId}/validate`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });

    expect(validationResponse.ok()).toBeTruthy();
    const validationData = await validationResponse.json();
    expect(validationData.valid_count).toBeGreaterThanOrEqual(0);
    expect(validationData.invalid_count).toBeGreaterThanOrEqual(0);
    expect(validationData.failure_breakdown).toBeDefined();
    expect(validationData.validated_at_utc).toBeTruthy();

    console.log(`Validation complete: ${validationData.valid_count} valid, ${validationData.invalid_count} invalid`);
    console.log(`Failure breakdown:`, validationData.failure_breakdown);

    // Verify validation outcomes persisted per VIN (FR-005)
    const totalValidated = validationData.valid_count + validationData.invalid_count;
    expect(totalValidated).toBe(extractionData.extracted_count);

    // Verify invalid VINs have explicit failure reasons (FR-005)
    if (validationData.invalid_count > 0) {
      const failureReasons = Object.keys(validationData.failure_breakdown);
      expect(failureReasons.length).toBeGreaterThan(0);
      
      // Expected failure reason codes from BR-01
      const validFailureReasons = ['wrong_length', 'invalid_character', 'checksum_failure', 'empty_value'];
      for (const reason of failureReasons) {
        if (validationData.failure_breakdown[reason] > 0) {
          expect(validFailureReasons).toContain(reason);
        }
      }
    }

    // ========================================
    // STEP 7: Verify Full Summary
    // ========================================
    const summaryResponse = await request.get(`/api/v1/vins/cases/${caseId}/summary`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
    });

    expect(summaryResponse.ok()).toBeTruthy();
    const summaryData = await summaryResponse.json();
    
    // Verify extraction summary (FR-004)
    expect(summaryData.extracted).toBe(extractionData.extracted_count);
    expect(summaryData.deduplicated).toBe(extractionData.deduplicated_count);
    expect(summaryData.rejected).toBe(extractionData.rejected_empty_count);
    
    // Verify validation summary (FR-005)
    expect(summaryData.valid).toBe(validationData.valid_count);
    expect(summaryData.invalid).toBe(validationData.invalid_count);
    expect(summaryData.failure_reason_breakdown).toEqual(validationData.failure_breakdown);

    console.log('Full summary verified:', summaryData);

    // ========================================
    // STEP 8: Verify Audit Trail
    // ========================================
    const auditResponse = await request.get(`/api/v1/audit/cases/${caseId}/events`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
    });

    expect(auditResponse.ok()).toBeTruthy();
    const auditEvents = await auditResponse.json();
    expect(Array.isArray(auditEvents)).toBeTruthy();
    
    // Verify minimum audit events for workflow:
    // 1. intake_registered
    // 2. attachment_parsed
    // 3. classification_recommendation_generated
    // 4. vins_extracted
    // 5. vins_validated
    expect(auditEvents.length).toBeGreaterThanOrEqual(5);

    console.log(`Audit trail contains ${auditEvents.length} events`);

    // Verify audit events contain expected action types
    const actionTypes = auditEvents.map((e: { action_type: string }) => e.action_type);
    expect(actionTypes).toContain('intake_submission');
    expect(actionTypes).toContain('attachment_parsed');
    expect(actionTypes).toContain('classification_recommendation');
    expect(actionTypes).toContain('vins_extracted');
    expect(actionTypes).toContain('vins_validated');

    // Verify audit events are ordered chronologically
    for (let i = 1; i < auditEvents.length; i++) {
      const prevTime = new Date(auditEvents[i - 1].occurred_at_utc).getTime();
      const currTime = new Date(auditEvents[i].occurred_at_utc).getTime();
      expect(currTime).toBeGreaterThanOrEqual(prevTime);
    }

    // Verify all audit events have required fields
    for (const event of auditEvents) {
      expect(event.correlation_id).toBeTruthy();
      expect(event.actor_type).toBeTruthy();
      expect(event.actor_id).toBeTruthy();
      expect(event.outcome).toBeTruthy();
    }

    // ========================================
    // FINAL: Navigate UI to verify visibility
    // ========================================
    
    // Navigate to audit page and verify events are visible
    await page.goto(`/audit/${caseAfterRecommendationData.case_key}`);
    await page.waitForLoadState('networkidle');
    
    // Verify audit page displays events
    const auditTable = page.locator('table').first();
    await expect(auditTable).toBeVisible();
    
    // Verify multiple event rows visible
    const auditRows = auditTable.locator('tbody tr');
    const rowCount = await auditRows.count();
    expect(rowCount).toBeGreaterThanOrEqual(5);

    console.log('✅ Journey test complete: Intake → Parsing → Classification Recommendation → Extraction → Validation → Audit');
  });
});
