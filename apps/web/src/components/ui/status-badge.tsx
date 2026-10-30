import * as React from "react"
import { cn } from "../../lib/utils"

export type SystemStatus =
  | "IDLE"
  | "RUNNING"
  | "IN_PROGRESS"
  | "SUCCESS"
  | "COMPLETED"
  | "WARNING"
  | "WAITING"
  | "BLOCKED"
  | "ERROR"
  | "FAILED"
  | string

interface StatusBadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  status: SystemStatus
  label?: string
  pulsing?: boolean
  size?: "sm" | "md"
}

export function StatusBadge({
  status,
  label,
  pulsing,
  size = "sm",
  className,
  ...props
}: StatusBadgeProps) {
  const norm = (status || "IDLE").toUpperCase().trim()

  let style = "border-cyan-500/30 bg-cyan-950/20 text-cyan-300"
  let dotColor = "bg-cyan-400"
  let defaultLabel = label || norm
  let isRunning = false

  if (norm === "RUNNING" || norm === "IN_PROGRESS" || norm === "EXECUTING" || norm === "EN CURSO") {
    style = "border-blue-500/40 bg-blue-950/30 text-blue-300 shadow-[0_0_12px_rgba(59,130,246,0.15)]"
    dotColor = "bg-blue-400"
    isRunning = true
  } else if (norm === "SUCCESS" || norm === "COMPLETED" || norm === "DONE" || norm === "READY" || norm === "LISTO") {
    style = "border-emerald-500/30 bg-emerald-950/20 text-emerald-300"
    dotColor = "bg-emerald-400"
  } else if (norm === "WARNING" || norm === "WAITING" || norm === "PENDING" || norm === "PAUSED" || norm === "GATE_REVIEW") {
    style = "border-amber-500/30 bg-amber-950/20 text-amber-300"
    dotColor = "bg-amber-400"
  } else if (norm === "BLOCKED" || norm === "ERROR" || norm === "FAILED" || norm === "CRITICAL") {
    style = "border-rose-500/30 bg-rose-950/20 text-rose-300"
    dotColor = "bg-rose-400"
  }

  const showPulse = pulsing !== undefined ? pulsing : isRunning

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border font-mono font-semibold transition-colors",
        size === "sm" ? "px-2.5 py-0.5 text-[10px]" : "px-3 py-1 text-xs",
        style,
        className
      )}
      {...props}
    >
      <span className="relative flex h-2 w-2">
        {showPulse && (
          <span
            className={cn(
              "absolute inline-flex h-full w-full animate-ping rounded-full opacity-75",
              dotColor
            )}
          />
        )}
        <span className={cn("relative inline-flex h-2 w-2 rounded-full", dotColor)} />
      </span>
      <span>{defaultLabel}</span>
    </div>
  )
}
