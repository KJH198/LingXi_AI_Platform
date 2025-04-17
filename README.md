# 灵犀AI智能体低代码开发平台

## 一、项目背景
$\qquad$在当今科技飞速发展的时代，AI 智能体已成为推动各行业变革的关键力量。从智能客服到智能推荐系统，从自动化流程到个性化学习辅助，AI 智能体的应用无处不在，展现出巨大的潜力与广阔的前景。然而，传统 AI 应用开发往往需要开发者具备深厚的编程知识和复杂的算法理解能力，这一高门槛限制了 AI 技术的普及与创新，尤其是对于渴望涉足 AI 领域的学生群体而言。\
$\qquad$低代码开发模式的出现，为解决这一难题带来了曙光。它通过可视化的操作界面和拖放式的组件，极大地简化了软件开发流程，使开发者能够在无需编写大量代码的情况下，快速搭建应用程序。这不仅显著提高了开发效率，还降低了开发成本，让更多人能够参与到软件开发中来，充分发挥自己的创意与想法。\
$\qquad$在此背景下，“灵犀” AI 智能体低代码开发平台应运而生。“灵犀” 专为非计算机专业的学生群体量身打造，旨在打破 AI 开发的技术壁垒，让他们即使没有深厚的编程基础，也能通过简洁直观的操作，轻松构建并部署各类 AI 智能体。通过 “灵犀” 平台，学生们能够在实践中激发对 AI 领域的创造力与探索欲，深入掌握 AI 智能体开发的核心要点，为未来投身 AI 行业奠定坚实的基础。

一键启动
```
cd .\FrontEnd\lingxi_ai_platform\ ; npm run build ; cd ..\..\registerAndLogin\ ; .\venv\Scripts\activate ; cd .. ; python .\registerAndLogin\manage.py runserver
```

CentOS一键启动
```
cd ./FrontEnd/lingxi_ai_platform/ && npm run build && cd ../../registerAndLogin/ && source venv/bin/activate && cd .. && nohup python3.9 ./registerAndLogin/manage.py runserver 0.0.0.0:8000 &
```