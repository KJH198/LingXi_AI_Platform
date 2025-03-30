# 灵犀AI低代码开发平台-前端部分说明

## 操作指导

### VSCode 插件安装

**VUE-Official**

### 环境配置(文件夹内运行一次即可)

```sh
npm install
```

### 启动服务器（前端开发）

```sh
npm run dev
```

### 生成部署文件（部署文件提供给后端）

```sh
npm run build
```

## 项目内容说明

### 根目录文件

#### 主要文件

node_modules：存放下载的依赖包

public：存放静态资源文件，如 favicon.ico（网站图标）

src ：项目源代码的主目录，包含 Vue 组件、样式和其他资源

​	-assets：存放静态资源文件，例如样式表和图片

​	-components：存放 Vue 组件

​	-App.vue：应用的根组件，定义了项目的整体结构

​	-main.ts：项目的入口文件，负责挂载根组件到 HTML 中的 #app

.gitignore：用于指定 Git 应该忽略的文件和文件夹，例如日志文件、node_modules、构建输出目录等

index.html：项目的入口 HTML 文件，Vite 会以此文件为模板注入脚本和样式



#### 次要文件

package.json：定义项目的依赖、脚本和元信息。包含运行开发服务器、构建项目等脚本

tsconfig.json：TypeScript配置文件，包含项目的基础配置和对其他配置文件的引用

​	-env.d.ts：声明文件，用于为 Vite 提供类型支持（不能删）

​	-tsconfig.app.json：为应用程序代码提供的 TypeScript 配置，指定了包含的文件和路径别名

​	-tsconfig.node.json：为 Node.js 环境相关文件提供的 TypeScript 配置，例如 Vite 配置文件

vite.config.ts：Vite的配置文件，定义了插件、路径别名等

.vscode/extensions.json：推荐的 VS Code 插件配置



#### 初始自动生成的文件（后面可能会删）

base.css：定义了全局的基础样式

main.css：定义了项目的主要样式，包含对 base.css 的引用。

logo.svg：项目的 logo

HelloWorld.vue：一个简单的组件，展示欢迎信息

TheWelcome.vue：包含多个 WelcomeItem 子组件，展示项目的功能介绍

WelcomeItem.vue：一个通用的组件，用于展示图标、标题和描述

icons/：存放图标组件，例如 IconCommunity.vue、IconDocumentation.vue 等
