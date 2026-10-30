import React, { useState, useEffect } from 'react'
import { WifiOff, RefreshCw } from 'lucide-react'

interface NetworkStatusBannerProps {
  onRetry?: () => void
}

export const NetworkStatusBanner: React.FC<NetworkStatusBannerProps> = ({ onRetry }) => {
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine)
  const [isReconnecting, setIsReconnecting] = useState<boolean>(false)

  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  if (isOnline) return null

  const handleManualRetry = () => {
    setIsReconnecting(true)
    onRetry?.()
    setTimeout(() => {
      setIsOnline(navigator.onLine)
      setIsReconnecting(false)
    }, 1500)
  }

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="bg-rose-500/15 border-b border-rose-500/40 text-rose-300 px-4 py-2 text-xs flex items-center justify-between gap-3 shrink-0 animate-fade-in"
    >
      <div className="flex items-center gap-2">
        <WifiOff className="w-4 h-4 text-rose-400 shrink-0" />
        <span className="font-semibold">
          Conexión al servidor SACL interrumpida. Reintentando reconexión automática...
        </span>
      </div>

      <button
        type="button"
        onClick={handleManualRetry}
        disabled={isReconnecting}
        className="px-3 py-1 rounded-lg bg-rose-600/30 hover:bg-rose-600/40 border border-rose-500/50 text-white font-mono text-[11px] flex items-center gap-1.5 transition cursor-pointer disabled:opacity-50"
      >
        <RefreshCw className={`w-3 h-3 ${isReconnecting ? 'animate-spin' : ''}`} />
        <span>{isReconnecting ? 'Verificando...' : 'Reintentar'}</span>
      </button>
    </div>
  )
}
