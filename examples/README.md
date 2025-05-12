# MarketGenius 使用示例

本目錄包含展示 MarketGenius 功能的示例代碼和資源文件。

## 示例文件

### 基本使用

- **[basic_usage.py](basic_usage.py)**: 展示如何使用 MarketGenius 生成簡單的行銷內容，包括文本生成、圖像提示詞生成和平台適配。

### 進階工作流程

- **[advanced_workflow.py](advanced_workflow.py)**: 展示更複雜的 MarketGenius 用例，包括品牌風格分析、多平台內容生成和使用代理系統協作創建完整行銷活動。

## 品牌樣本

`brand_samples/` 目錄包含用於品牌風格分析的示例內容：

- **[about_us.txt](brand_samples/about_us.txt)**: 品牌介紹內容
- **[blog_post.txt](brand_samples/blog_post.txt)**: 品牌部落格文章範例
- **[social_post.txt](brand_samples/social_post.txt)**: 品牌社交媒體貼文範例

這些樣本用於訓練系統識別品牌的獨特風格特徵，以便生成風格一致的內容。

## 運行示例

運行這些示例前，請確保：

1. 已安裝所有必要的依賴項（參見主目錄中的 `requirements.txt`）
2. 設置了有效的 OpenAI API 密鑰（可通過環境變量 `OPENAI_API_KEY` 設置）
3. 已在本地安裝 MarketGenius 包或已將其添加到 Python 路徑中

運行示例：

```bash
# 基本示例
python examples/basic_usage.py

# 進階工作流程示例
python examples/advanced_workflow.py
```

## 注意事項

- 這些示例僅用於演示目的，實際應用中可能需要調整代碼以適應特定需求
- 某些功能可能需要額外的 API 密鑰或服務配置
- 生成的內容質量取決於提供的品牌樣本質量和數量
