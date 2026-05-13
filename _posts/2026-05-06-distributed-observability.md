---
layout: post
title: "构建可观测的分布式系统：从 Metrics 到 Tracing 的演进之路"
date: 2026-05-06
tags: [Observability, Distributed, OpenTelemetry]
read_time: "6 分钟"
---

OpenTelemetry 如何统一了可观测性的三大支柱？通过一个真实的微服务案例，展示从零搭建分布式追踪的最佳实践与踩坑记录。

## 可观测性的三大支柱

可观测性（Observability）是现代分布式系统的核心能力。它由三个关键支柱组成：

- **Metrics（指标）**：聚合数据，告诉你系统是否健康
- **Tracing（追踪）**：请求在系统中的完整路径
- **Logging（日志）**：离散的事件记录

## OpenTelemetry 的定位

OpenTelemetry 不是一个可观测性后端，而是一个统一的数据采集标准。它定义了如何生成、收集和导出遥测数据，让开发者可以在不锁定厂商的情况下，自由选择后端。

## 实战案例

我们在一个包含 12 个微服务的电商系统中引入了 OpenTelemetry。关键步骤包括：

1. 自动注入（Auto-instrumentation）覆盖了 80% 的需求
2. 手动埋点覆盖了核心业务流程
3. 使用 Jaeger 作为本地开发环境的追踪后端
4. 生产环境切换到 Grafana Tempo

## 踩坑记录

- 采样策略需要根据流量调整，全量采集在大流量下会严重影响性能
- Context Propagation 在异步消息队列场景下需要手动处理
