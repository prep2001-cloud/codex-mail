#!/bin/bash

# NEXXBot API 使用示例
# 确保服务已启动: python main.py

API_URL="http://localhost:8000"

echo "========================================="
echo "NEXXBot API 使用示例"
echo "========================================="

# 1. 健康检查
echo -e "\n1️⃣  健康检查"
curl -s "${API_URL}/health" | jq .

# 2. 列出所有智能体
echo -e "\n2️⃣  列出所有智能体"
curl -s "${API_URL}/agents" | jq .

# 3. 数据分析任务
echo -e "\n3️⃣  数据分析任务"
curl -s -X POST "${API_URL}/task" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "统计本月设备耗电量，对比每层能耗差异，并分析原因",
    "context": {
      "warehouse_id": "WH001",
      "month": "2024-10"
    }
  }' | jq .

# 4. 运营任务（ASN创建）
echo -e "\n4️⃣  运营任务（ASN创建）"
curl -s -X POST "${API_URL}/task" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "创建入库单：供应商DELTA，商品UltraPure Hand Soap，数量8件，交货日期2024-10-05",
    "context": {
      "operation_type": "create_asn"
    }
  }' | jq .

# 5. 销售咨询
echo -e "\n5️⃣  销售咨询"
curl -s -X POST "${API_URL}/task" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "你们有适合存放食品的仓库吗？温度多少？",
    "context": {
      "channel": "whatsapp",
      "customer_id": "CUST001"
    }
  }' | jq .

# 6. 查看智能体状态
echo -e "\n6️⃣  查看 Annexx 智能体状态"
curl -s "${API_URL}/agents/annexx/status" | jq .

# 7. 添加知识到知识库
echo -e "\n7️⃣  添加知识到知识库"
curl -s -X POST "${API_URL}/knowledge/add" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "仓库温控范围：冷冻-22°C，冷藏+2至+7°C，恒温+24°C",
      "贴标服务价格：0.71里亚尔每件，不含物料成本"
    ],
    "metadata": [
      {"type": "warehouse_info", "category": "temperature"},
      {"type": "pricing", "category": "value_added_service"}
    ]
  }' | jq .

# 8. 搜索知识库
echo -e "\n8️⃣  搜索知识库"
curl -s -X POST "${API_URL}/knowledge/search?query=温度&n_results=3" \
  -H "Content-Type: application/json" | jq .

# 9. 快速示例 - 数据分析
echo -e "\n9️⃣  快速示例 - 数据分析"
curl -s -X POST "${API_URL}/examples/data-analysis" | jq .

# 10. 快速示例 - 运营自动化
echo -e "\n🔟 快速示例 - 运营自动化"
curl -s -X POST "${API_URL}/examples/operations" | jq .

echo -e "\n========================================="
echo "所有示例执行完成！"
echo "========================================="
