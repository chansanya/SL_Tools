import { forwardRef, useImperativeHandle, useRef, useState } from 'react'

export interface ToastHandle {
  show: (text: string, kind?: 'info' | 'success' | 'error') => void
}

interface ToastItem {
  id: number
  text: string
  kind: 'info' | 'success' | 'error'
}

const Toast = forwardRef<ToastHandle>(function Toast(_props, ref) {
  const [items, setItems] = useState<ToastItem[]>([])
  const seq = useRef(0)

  useImperativeHandle(ref, () => ({
    show(text: string, kind: 'info' | 'success' | 'error' = 'info'): void {
      const id = ++seq.current
      setItems((prev) => [...prev, { id, text, kind }])
      setTimeout(() => setItems((prev) => prev.filter((t) => t.id !== id)), 2600)
    }
  }))

  return (
    <div className="toast-wrap">
      {items.map((t) => (
        <div key={t.id} className={`toast toast-${t.kind}`}>
          {t.text}
        </div>
      ))}
    </div>
  )
})

export default Toast
