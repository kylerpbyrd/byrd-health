import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceArea,
  ComposedChart,
  Legend,
  type TooltipProps,
} from "recharts";

import type { ChartData } from "@/types/fertility";

interface BBTChartProps {
  chartData: ChartData;
  height?: number;
  mini?: boolean;
}

interface DataPoint {
  label: string;
  temp: number | null;
  dayIndex: number;
}

export function BBTChart({ chartData, height = 350, mini = false }: BBTChartProps) {
  const data: DataPoint[] = chartData.labels.map((label, i) => ({
    label,
    temp: chartData.temperatures[i] ?? null,
    dayIndex: i,
  }));

  const discardedPoints = chartData.discarded.map((d) => {
    const idx = chartData.labels.indexOf(d.x);
    return { label: d.x, temp: d.y, dayIndex: idx >= 0 ? idx : 0 };
  });

  const validData = data.filter((d) => d.temp !== null);
  const temps = validData.map((d) => d.temp as number);
  const minTemp = temps.length > 0 ? Math.floor(Math.min(...temps) * 100) / 100 - 0.3 : 97;
  const maxTemp = temps.length > 0 ? Math.ceil(Math.max(...temps) * 100) / 100 + 0.3 : 99;

  const yTickFormatter = (val: number) => `${val.toFixed(1)}°${chartData.unit}`;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const customTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const p = payload[0].payload;
      const dayNum = p.dayIndex + 1;
      const mucus = chartData.mucus[p.label];
      const opk = chartData.opk[p.label];
      return (
        <div className="rounded-md border bg-white p-2 text-xs shadow-lg">
          <p className="font-semibold">
            Day {dayNum} ({p.label})
          </p>
          <p>
            Temp: {p.temp?.toFixed(2)}°{chartData.unit}
          </p>
          {mucus && <p>Mucus: {mucus.replace("_", " ")}</p>}
          {opk && <p>OPK: {opk}</p>}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full" role="img" aria-label="Basal Body Temperature chart">
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={[minTemp, maxTemp]}
            tick={{ fontSize: 11 }}
            tickFormatter={yTickFormatter}
            tickLine={false}
            axisLine={false}
            width={55}
          />
          <Tooltip content={customTooltip} />
          {!mini && <Legend />}

          {!mini && chartData.fertile_start_day !== null && chartData.fertile_end_day !== null && (
            <ReferenceArea
              x1={chartData.labels[chartData.fertile_start_day]}
              x2={chartData.labels[chartData.fertile_end_day]}
              fill="#22c55e"
              fillOpacity={0.1}
              label={{
                value: "Fertile",
                position: "insideTop",
                fontSize: 10,
                fill: "#22c55e",
              }}
            />
          )}

          {chartData.coverline !== null && (
            <ReferenceLine
              y={chartData.coverline}
              stroke="#ef4444"
              strokeDasharray="6 4"
              strokeWidth={1.5}
              label={
                !mini
                  ? {
                      value: `Coverline ${chartData.coverline.toFixed(2)}`,
                      position: "right",
                      fontSize: 10,
                      fill: "#ef4444",
                    }
                  : undefined
              }
            />
          )}

          {!mini &&
            chartData.ovulation_day !== null &&
            chartData.ovulation_day < chartData.labels.length && (
              <ReferenceLine
                x={chartData.labels[chartData.ovulation_day]}
                stroke="#f97316"
                strokeWidth={1.5}
                label={{
                  value: "Ovulation",
                  position: "top",
                  fontSize: 10,
                  fill: "#f97316",
                }}
              />
            )}

          <Line
            type="monotone"
            dataKey="temp"
            name="Temperature"
            stroke="#9c27b0"
            strokeWidth={2}
            dot={{ r: 3, fill: "#9c27b0", stroke: "#fff", strokeWidth: 1 }}
            activeDot={{ r: 5, fill: "#9c27b0", stroke: "#fff", strokeWidth: 2 }}
            connectNulls
          />

          {discardedPoints.length > 0 && (
            <Line
              data={discardedPoints}
              dataKey="temp"
              name="Discarded"
              stroke="none"
              dot={{ r: 3, fill: "#9ca3af", stroke: "#6b7280", strokeWidth: 1 }}
              legendType="none"
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
