import { Card, CardContent } from "@/components/ui/card";

interface StatTileProps {
  value: string | number;
  label: string;
  subtext?: string;
}

export function StatTile({ value, label, subtext }: StatTileProps) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center p-4 text-center">
        <span className="text-2xl font-bold text-primary">
          {value ?? "—"}
        </span>
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
        {subtext && (
          <span className="mt-1 text-xs text-muted-foreground">{subtext}</span>
        )}
      </CardContent>
    </Card>
  );
}
