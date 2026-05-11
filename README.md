# pve-ui

基于 Django REST Framework 和 Vue 3 的 PVE 集群管理系统，提供统一的 PVE 资源管理和操作界面。

http://token.ctfzone.cloud/ 
不是按 Token 计费，而是按天收费 任性用 吃到饱

传统平台用多少 Token 算多少钱，我们改成日订阅：按天开通，当天不限量使用。 适合高频调用、长期跑任务、团队持续开发。

![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)
![Django Version](https://img.shields.io/badge/django-5.2.7-green.svg)
![Vue Version](https://img.shields.io/badge/vue-3.5.22-brightgreen.svg)

## 作者
wx: rz1433 | qq: 1433711899


## 📌 版本说明

**本项目分为两个版本：**

- **社区版本**：GitHub 开源版本，完全免费使用
- **运维版本**：群友付费推出的版本，需要激活码才能使用 联系作者获取 目前免费一个月体验 
- && 定价策略为卖服务 1:单运维版本授权年费 199 赠送定制需求1个 2:运维版本授权年费+定制化需求2到3个 399 3:运维版本永久授权1200+赠送定制化需求6-8个
- 二开一个功能的价格市场价格很透明 定价应该没问题

**运维版本说明：**

项目中的 `docker-compose-devops.yaml` 是**运维版本**，需要激活码才能使用。如需使用该版本，请联系作者获取激活码。

**联系方式**：
- 微信：rz1433
- QQ：1433711899

## ✨ 核心功能

### 🖧 PVE 管理
- **PVE 服务器管理**：统一维护多套 PVE API Token、SSL 校验、可用状态
- **虚拟机全生命周期**：创建、克隆、备份、快照、同步、任务日志等一站式操作
- **节点与存储监控**：实时查看节点资源、全局任务、模板与 ISO 存储内容
- **网络拓扑编排**：基于 LogicFlow 的拖拽式拓扑设计器，可保存/加载网络结构并与 PVE 资源关联

### 🔐 权限管理
- **RBAC 权限控制**：基于角色的访问控制，支持菜单、按钮级别权限
- **数据权限**：支持组织级数据隔离，可按组织、用户过滤数据

## 🛠️ 技术栈

### 后端
- Django 5.2.7 + Django REST Framework
- djangorestframework-simplejwt (JWT 认证)
- APScheduler (任务调度)
- MySQL/SQLite

### 前端
- Vue 3 + Vite
- Arco Design (UI 组件库)
- Vue Router + Vuex
- LogicFlow (网络拓扑)

## 🚀 快速开始

### 环境要求
- Python 3.12+
- Node.js 22+
- MySQL 8.0+ (可选，默认使用 SQLite)

### 后端安装

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

pip install -r requirements.txt
python manage.py migrate
python manage.py init_rbac --create-superuser
python manage.py runserver
```

后端服务将在 `http://127.0.0.1:8000` 启动

### 前端安装

```bash
cd front-end
npm install
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

### 默认账号
- **用户名**: `admin`
- **密码**: `admin123`

## 🐳 Docker 部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

访问地址：
- **前端**: http://localhost
- **后端 API**: http://localhost:8000

> **注意**：`docker-compose-devops.yaml` 是运维版本，需要激活码。详见上方 [版本说明](#-版本说明)。


## 📸 功能截图&交流群
![交流群](images/8a680cb614758f6dbf4d20df46d3399b.jpg)
![PVE管理](images/截屏2025-11-27%2010.25.14.png)
![PVE节点](images/截屏2025-11-28%2010.05.33.png)
![虚拟机管理](images/截屏2025-11-28%2010.10.32.png)
![存储管理](images/截屏2025-11-28%2010.11.06.png)
![网络拓扑](images/截屏2025-11-28%2010.11.23.png)
![任务管理](images/截屏2025-11-28%2010.11.51.png)

## 🙏 致谢

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue.js](https://vuejs.org/)
- [Arco Design](https://arco.design/)

---
## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=niezhicheng/pveui&type=date&legend=top-left)](https://www.star-history.com/#niezhicheng/pveui&type=date&legend=top-left)


**⭐ 如果这个项目对你有帮助，请给个 Star！如果您想赞助本项目扫下面的码**
## 📸 赞赏码
![微信](images/5d022d43e6fd2393b7ef72bd0e3dc793.jpg)
![支付宝](images/a0699a1b9ae07770f8761df4a6634f11.jpg)
