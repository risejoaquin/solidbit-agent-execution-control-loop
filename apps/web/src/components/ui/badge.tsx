import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-mono font-semibold transition-colors focus:outline-none",
  {
    variants: {
      variant: {
        default: "border border-zinc-700 bg-zinc-900 text-zinc-200",
        solid: "bg-white text-black font-extrabold shadow-sm",
        success: "border border-emerald-500/30 bg-emerald-950/20 text-emerald-300",
        warning: "border border-amber-500/30 bg-amber-950/20 text-amber-300",
        danger: "border border-red-500/30 bg-red-950/20 text-red-400",
        idle: "border border-zinc-800 bg-zinc-900 text-zinc-400",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}
