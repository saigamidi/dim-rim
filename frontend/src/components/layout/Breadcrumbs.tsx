/**
 * Breadcrumb navigation component matching wireframe design.
 */

import { ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export function Breadcrumbs({ items }: BreadcrumbsProps) {
  return (
    <div className="flex gap-s2 items-center text-sm text-muted mb-s3">
      {items.map((item, index) => (
        <span key={index} className="flex items-center gap-s2">
          {item.href ? (
            <Link to={item.href} className="text-accent hover:underline">
              {item.label}
            </Link>
          ) : (
            <span>{item.label}</span>
          )}
          {index < items.length - 1 && <ChevronRight className="w-4 h-4" />}
        </span>
      ))}
    </div>
  );
}
