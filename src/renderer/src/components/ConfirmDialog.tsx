import { forwardRef, useImperativeHandle, useRef, useState } from 'react'

export interface ConfirmHandle {
  ask: (title: string, message: string) => Promise<boolean>
}

interface InternalState {
  open: boolean
  title: string
  message: string
}

const ConfirmDialog = forwardRef<ConfirmHandle>(function ConfirmDialog(_props, ref) {
  const [state, setState] = useState<InternalState>({ open: false, title: '', message: '' })
  const resolveRef = useRef<(v: boolean) => void>(() => {})

  useImperativeHandle(ref, () => ({
    ask(title: string, message: string): Promise<boolean> {
      setState({ open: true, title, message })
      return new Promise<boolean>((resolve) => {
        resolveRef.current = resolve
      })
    }
  }))

  const close = (v: boolean): void => {
    setState((s) => ({ ...s, open: false }))
    resolveRef.current(v)
  }

  if (!state.open) return null

  return (
    <div className="modal-mask" onClick={() => close(false)}>
      <div className="modal card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-title">{state.title}</div>
        <div className="modal-msg">{state.message}</div>
        <div className="row" style={{ justifyContent: 'flex-end' }}>
          <button className="btn btn-ghost" onClick={() => close(false)}>
            取消
          </button>
          <button className="btn btn-primary" onClick={() => close(true)}>
            确定
          </button>
        </div>
      </div>
    </div>
  )
})

export default ConfirmDialog
