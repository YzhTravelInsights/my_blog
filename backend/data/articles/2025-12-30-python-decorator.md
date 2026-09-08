---
title: "Python 装饰器从入门到装逼"
date: 2025-12-30
category: Python
tags: ["Python", "装饰器", "进阶"]
summary: "用大白话讲清 Python 装饰器：闭包、语法糖、带参装饰器、functools.wraps。"
---

## 先搞清楚闭包

装饰器的一切都建立在**闭包**之上：函数可以返回函数，内层函数能记住外层函数的变量。

```python
def outer(x):
    def inner():
        return x * 2
    return inner

f = outer(21)
print(f())  # 42
```

## 装饰器就是语法糖

```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"耗时 {time.time() - start:.4f}s")
        return result
    return wrapper

@timer
def slow_add(a, b):
    time.sleep(0.1)
    return a + b
```

`@timer` 等价于 `slow_add = timer(slow_add)`。

## 带参数与保留元信息

- 带参装饰器：外面再包一层函数
- `functools.wraps`：保留原函数的 `__name__`、`__doc__`

## 真实场景

- 鉴权中间件
- 日志埋点
- 重试逻辑

## 小结

装饰器是 Python 里最优雅的语言特性之一。理解闭包之后，它就是一层窗户纸。
