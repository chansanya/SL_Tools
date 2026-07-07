import ReactDOM from 'react-dom/client'
import { ConfigProvider, App as AntApp } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from './App'
import './styles/global.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <ConfigProvider
    locale={zhCN}
    theme={{
      token: {
        colorPrimary: '#4f8cff',
        borderRadius: 8,
        fontFamily:
          "'PingFang SC','Microsoft YaHei UI','Microsoft YaHei','Segoe UI',system-ui,sans-serif"
      }
    }}
  >
    <AntApp style={{ height: '100%' }} component={false}>
      <App />
    </AntApp>
  </ConfigProvider>
)
