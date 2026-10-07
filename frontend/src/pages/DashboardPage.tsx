import { CostComparison } from '../components/Dashboard/CostComparison';

export function DashboardPage() {
  return (
    <div className="flex-1 overflow-y-auto px-6 py-10">
      <div className="max-w-xl mx-auto">
        <h1 className="text-lg font-semibold mb-6" style={{ color: 'var(--color-text)' }}>
          Dashboard
        </h1>
        <CostComparison />
      </div>
    </div>
  );
}
