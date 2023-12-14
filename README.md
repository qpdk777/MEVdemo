# 导论

# 算法设计

## 问题重述

一个封闭系统中的转账请求由一个 MEV 机器人进行记录。机器人可以随意安排 Request 之间的顺序，而在一个 Request 内部需要保持 Transfer 的相对顺序。机器人可以选择性地执行交易与转账。

**约束条件 1**：任何时候任何用户的资产都不能是负值。

**约束条件 2**：同一个 Request 内部的 Transfer 需要保持相对顺序不变。

## 目标

实现机器人的收益最大化。

## 推导过程

**公理 1**：整个系统的资金量守恒。

机器人的收益完全来源于用户支付的 fee ，要实现机器人收益最大化，等效于让全体用户的资产最小化。我们的目标就是让所有用户尽可能变穷。

**公理 2**：在不违背约束条件 1 的情况下，机器人应当尽可能多地记录交易。

显然可以证明，这样做不会使答案变坏。

**公理 3**：对于任何一个确定的系统状态，如果存在能够立刻支付所有转出交易的用户（称之为财富自由者），机器人可以并应当直接执行这些交易。

可行性：此时执行这些交易，不会导致财富自由者余额变为负值，不违背约束条件 1 。同时，新插入的交易也不会违背约束条件 2 。

最优性：这样做能够尽可能地把资金转移到非财富自由者手中，使得他们的余额变大以便能够支付更多其他交易。

**推论**：此后，其他转入财富自由者的转账应当被置于次要考虑地位。

因为财富自由者不再有转出的转账了，无法为我们提供更多价值，向他们转账会导致转账资金退出流通领域。如果这样的转账并没有巨大的 fee 作为激励，机器人不应该予以考虑。

**公理 4**：对于任何一个确定的系统状态，如果没有财富自由者，在剩余的交易集中，如果 fee 最大的那一笔转账可以被立即执行，那么就应该立即执行，且这样的转账要尽可能早地执行。

因为这样可以在赚取较大收益的同时，让尽可能多的资金尽可能早地流向其他用户，为机器人后续获利提供更多可能性。

此外，我们近似地认为 $MEV$ 函数在 request 的排列空间内具有连续性。

这就是说，对一个 request 排列 $P_1=\{r_1,r_2,...,r_i,...,r_j,...,r_n\}$ 交换两个 $(r_i,r_j)(i<j)$ 得到新排列 $P_2=\{r_1,r_2,...,r_j,...,r_i,...,r_n\}$ ，其 $MEV(P_2)$ 与原 $MEV(P_1)$ 接近。

这是因为交换两个 request 绝对不会影响到他们之前的交易，而他们之后的交易虽然可能会发生改变（一部分转账可能变得不可行，而另一部分转账可能会变得可行且提供更大价值），但考虑到 $r_i$ 之前的交易排列只发生了微小的改变， $r_i$ 完成后系统的状态与原排列中 $r_j$ 完成后的状态仅有微小差别。

## 算法描述

使用模拟退火寻找最优的 request 排列。

1. 设初始温度为 $T$ ，退火速率为 $k$ 
2. 随机生成一个排列 $P_0$ ，其 MEV 为 $MEV(P_0)$ 
3. 随机选择 $(i,j)$ 并交换 $r_i,r_j$ 得到 $P_1$
4. 比较 $MEV(P_1)$ 与 $MEV(P_0)$ ，根据 Metropolis 准则判断是否接受 $P_1$ 
5. 退火，并回到第 3 步；如果温度达到临界值 $\varepsilon$ ，结束

如果请求集的规模很大，交换两个 request 这种微小的扰动几乎不可能对总体结果产生很坏的影响。

如果请求集的规模较小，模拟退火就能够比较高效地在所有状态空间中找到一个局部最优解。

对于一个确定的 request 排列，使用贪心算法寻找最优的转账集。

1. 执行所有财富自由者发出的转账，将其从转账集中剔除
2. 将转账集按照 fee 降序排序
3. 找到 fee 最高的合法的转账，执行，并将其从转账集中剔除；如果所有转账都不合法，结束
4. 回到第 2 步

值得注意的是，排序与剔除的过程可以使用堆、红黑树等数据结构进行优化。出于时间原因，本次实现不包含此优化。如果具有足够的时间，实现这些数据结构对本人来说不在话下。

## 复杂度分析

对于一个确定的 request ，如果转账集大小为 $n$ ，那么寻找最优转账集的时间复杂度为 $O(n\log n)$ ，是相当令人满意的复杂度。

模拟退火的复杂度取决于初始温度、退火速率和临界值的选择，其复杂度为 $\displaystyle O(\log_k \frac{\varepsilon}{T})$ 

总体复杂度为 $\displaystyle O(\log_k \frac{\varepsilon}{T} \cdot n\log n)$ ，应当根据实际应用场景的数据规模、响应时间要求合理设置参数。

# 异常处理

如果某一笔转账的 amount 或 fee 不是非负的数字，删除该笔转账。

如果某一笔转账的 from 和 to 不在初始化的用户集中，删除该笔转账。

若某一个请求为空，删除该请求。