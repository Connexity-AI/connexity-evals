'use client';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@workspace/ui/components/ui/table';
import { Skeleton } from '@workspace/ui/components/ui/skeleton';

import { TablePaginationSkeleton } from '@/components/common/data-table/table-pagination-skeleton';

// Row height matches the real AgentsTable row (measured at 52.8px). Fixing the
// height here keeps the skeleton from jumping vertically when real data
// arrives and the rows settle to their final measurements.
const ROW_HEIGHT = '52.8px';

interface AgentsTableSkeletonProps {
  rows?: number;
}

export function AgentsTableSkeleton({ rows = 8 }: AgentsTableSkeletonProps) {
  return (
    <div className="flex flex-1 flex-col min-w-0">
      <div className="flex-1 overflow-auto p-6">
        <div className="overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>
                  <Skeleton className="h-4 w-20" />
                </TableHead>
                <TableHead>
                  <Skeleton className="h-4 w-24" />
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {Array.from({ length: rows }).map((_, index) => (
                <TableRow
                  key={index}
                  className="hover:bg-transparent"
                  style={{ height: ROW_HEIGHT }}
                >
                  <TableCell>
                    <Skeleton className="h-4 w-40" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-36" />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <div className="border-t border-border px-4 py-3">
            <TablePaginationSkeleton />
          </div>
        </div>
      </div>
    </div>
  );
}
