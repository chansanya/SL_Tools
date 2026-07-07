/** 自定义无边框标题栏: 拖拽区 + 品牌 + 最小化/最大化/关闭按钮 */
export default function TitleBar(): JSX.Element {
  return (
    <div className="titlebar">
      <div className="titlebar-brand">SL 存档工具</div>
      <div className="titlebar-controls">
        <button
          className="tb-btn"
          title="最小化"
          onClick={() => window.api.minimize()}
        >
          <svg width="11" height="11" viewBox="0 0 11 11">
            <path d="M1 5.5h9" stroke="currentColor" strokeWidth="1.2" />
          </svg>
        </button>
        <button
          className="tb-btn"
          title="最大化/还原"
          onClick={() => window.api.toggleMaximize()}
        >
          <svg width="11" height="11" viewBox="0 0 11 11">
            <rect x="1.5" y="1.5" width="8" height="8" stroke="currentColor" strokeWidth="1.2" fill="none" />
          </svg>
        </button>
        <button
          className="tb-btn tb-close"
          title="关闭"
          onClick={() => window.api.closeWindow()}
        >
          <svg width="11" height="11" viewBox="0 0 11 11">
            <path d="M1.5 1.5l8 8M9.5 1.5l-8 8" stroke="currentColor" strokeWidth="1.3" />
          </svg>
        </button>
      </div>
    </div>
  )
}
