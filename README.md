# MarketGenius(實驗階段)

MarketGenius 是一個AI驅動的多平台行銷內容生成系統，專為台灣中小企業設計。

## 主要功能

- **品牌特色分析**：從既有內容中提取並學習品牌獨特風格和語調
- **多平台內容生成**：同時為Instagram、Facebook、LinkedIn、YouTube生成定制內容
- **多代理協作**：專業分工的AI代理團隊，模擬完整行銷團隊協作流程
- **多模態生成**：文字、圖像、短影片一站式生成
- **效果分析與優化**：基於互動數據提供優化建議

## 安裝指南

### 環境要求

- Python 3.9+
- 支援的作業系統：Windows, macOS, Linux

### 安裝步驟

1. 克隆倉庫
   ```bash
   git clone https://github.com/marketgenius/marketgenius.git
   cd marketgenius

2. 安裝依賴
   ```bash
   pip install -r requirements.txt

3. 設置API密鑰
   創建 .env 文件並添加以下內容:
   ```
   OPENAI_API_KEY=your_openai_api_key
   STABILITY_API_KEY=your_stability_api_key

4. 運行應用
   ```bash
   python -m marketgenius.main

### 模擬Demo

1.內容生成
[![YouTube](http://i.ytimg.com/vi/18bRwR1fACc/hqdefault.jpg)](https://www.youtube.com/watch?v=18bRwR1fACc)
