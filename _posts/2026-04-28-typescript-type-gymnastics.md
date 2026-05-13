---
layout: post
title: "TypeScript 类型体操进阶：从泛型到模板字面量类型的实战技巧"
date: 2026-04-28
tags: [TypeScript, Types, Advanced]
read_time: "7 分钟"
---

不止于基础泛型——深入条件类型、映射类型与模板字面量类型的组合使用。通过一个类型安全的 API 路由推导器，展示高级类型编程的真实威力。

## 基础回顾

TypeScript 的类型系统是图灵完备的。这意味着你可以在类型层面进行程序化的类型推导。

核心工具：
- **条件类型**：`T extends U ? X : Y`
- **映射类型**：`{ [K in keyof T]: ... }`
- **模板字面量类型**：`` `${Prefix}${string}` ``

## 实战：类型安全的 API 路由

我们来实现一个能从路由字符串推导出参数和返回类型的系统：

```typescript
type Route = '/users/:id/posts/:postId'
type Params = ExtractParams<Route>
// { id: string; postId: string }
```

通过组合递归条件类型和模板字面量类型，可以实现编译时的路由参数推导，彻底消除运行时字符串拼接错误。

## 性能注意事项

类型体操虽好，但过度复杂的类型推导会显著增加编译时间。建议将复杂类型拆分成独立文件，并设置合理的复杂度上限。
