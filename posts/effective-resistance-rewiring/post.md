---
layout: post
title: "Effective Resistance Rewiring: A Simple Topological Correction for Over-Squashing"
description: "We study over-squashing in Graph Neural Networks as a topology-driven bottleneck and use effective resistance to guide controlled graph rewiring."
date: 2026-05-07
categories: research graph-neural-networks
tags: gnn oversquashing graph-rewiring effective-resistance pairnorm iclr gram
---

<div class="post-info">
  <strong>Paper:</strong> Effective Resistance Rewiring: A Simple Topological Correction for Over-Squashing<br>
  <strong>Venue:</strong> GRaM Workshop at ICLR 2026, Proceedings Track<br>
  <strong>Authors:</strong> Bertran Miquel-Oliver, Manel Gil-Sorribes, Victor Guallar, Alexis Molina<br>
  <strong>arXiv:</strong> <a href="https://arxiv.org/abs/2603.11944" target="_blank">2603.11944</a>
</div>

Graph Neural Networks (GNNs) update node representations by aggregating information from neighboring nodes. This message-passing mechanism gives GNNs a strong inductive bias for relational data, but it also constrains how information can propagate through a graph <d-cite key="KipfWelling2017GCN"></d-cite>.

When useful information is far away, a GNN needs multiple layers to propagate it. However, increasing depth does not automatically solve long-range reasoning. If many distant nodes can influence a target node only through a narrow set of intermediate nodes or edges, their information has to be compressed into fixed-size vectors. This can strongly attenuate long-range signals.

This phenomenon is known as **over-squashing** <d-cite key="AlonYahav2020"></d-cite>.

In our GRaM workshop paper at ICLR 2026, **Effective Resistance Rewiring: A Simple Topological Correction for Over-Squashing**, we study over-squashing as a topology-driven limitation and propose a graph rewiring strategy based on **effective resistance** <d-cite key="BlackEtAl2023"></d-cite>.

The central question is:

> Can we modify graph topology so that long-range information has better routes to propagate through a GNN?

## Over-squashing and oversmoothing

Deep message passing is affected by two related but distinct phenomena.

**Over-squashing** occurs when information from a rapidly growing receptive field has to pass through structural bottlenecks and be compressed into fixed-size node representations <d-cite key="AlonYahav2020"></d-cite><d-cite key="DiGiovanniEtAl2023WidthDepth"></d-cite>.

**Oversmoothing** occurs when repeated aggregation makes node embeddings increasingly similar, reducing their discriminative power <d-cite key="LiHanWu2018"></d-cite><d-cite key="RuschEtAl2023OversmoothingSurvey"></d-cite>.

These two effects interact. Adding edges can help reduce over-squashing by creating alternative communication paths, but it can also increase mixing and accelerate oversmoothing. Therefore, topology correction should not simply densify the graph. It should improve weak communication pathways while controlling unnecessary mixing <d-cite key="GiraldoEtAl2023Tradeoff"></d-cite>.

## Effective resistance as a bottleneck signal

To identify structural bottlenecks, we use **effective resistance**.

Effective resistance comes from the electrical-network analogy: a graph can be viewed as a network where edges act like wires and information can flow through all available paths <d-cite key="DoyleSnell1984"></d-cite><d-cite key="KleinRandic1993"></d-cite>. If two nodes are connected by many alternative routes, their effective resistance is low. If communication between them depends on narrow bottlenecks, their effective resistance is high.

This makes effective resistance useful for studying over-squashing because it captures global, multi-path connectivity rather than only shortest-path distance or local neighborhood structure.

For an undirected connected graph with Laplacian \(L\), the effective resistance between nodes \(i\) and \(j\) is:

\[
R_{ij} = (e_i - e_j)^\top L^\dagger (e_i - e_j),
\]

where \(L^\dagger\) is the Moore-Penrose pseudoinverse of the graph Laplacian.

Large values of \(R_{ij}\) indicate weak multi-path connectivity, which is consistent with bottlenecked information transmission. Effective resistance has also been connected to over-squashing through bounds on message-passing influence <d-cite key="BlackEtAl2023"></d-cite>.

## Effective Resistance Rewiring

We propose **Effective Resistance Rewiring (ERR)**, a controlled add-remove rewiring strategy.

At each rewiring step:

1. Find the node pair with the largest effective resistance.
2. Add an edge to improve this weak communication pathway.
3. Find an edge with very small effective resistance.
4. Remove that edge only if connectivity is preserved.

The goal is to strengthen poorly connected regions while avoiding uncontrolled graph densification.

The method is parameter-free beyond the rewiring budget. The budget controls the number of allowed edge edits.

## Experimental setting

We evaluate the method on node classification datasets with different graph regimes:

- **Homophilic graphs:** Cora and CiteSeer
- **Heterophilic graphs:** Cornell and Texas

We study GCNs on undirected settings and DirGCN in directed settings <d-cite key="TongEtAl2020DirGCN"></d-cite>. We also compare models with and without **PairNorm**, a normalization method designed to mitigate oversmoothing <d-cite key="ZhaoAkoglu2019PairNorm"></d-cite>.

The experiments analyze:

- test accuracy as depth increases,
- the interaction between rewiring and PairNorm,
- linear-probe accuracy on penultimate-layer embeddings <d-cite key="alain2016understanding"></d-cite>,
- cosine similarity between same-class and different-class node embeddings,
- CKA similarity between representations learned under different rewiring strategies <d-cite key="kornblith2019similarity"></d-cite>.

Datasets and splits are loaded through PyTorch Geometric <d-cite key="fey2019fast"></d-cite>.

## Accuracy across depth

The first set of results studies GCN test accuracy as the number of layers increases.

On homophilic citation graphs such as Cora and CiteSeer, accuracy tends to degrade with depth when PairNorm is not used. This is consistent with oversmoothing in deeper models. PairNorm stabilizes the depth trend and reduces the sharp degradation observed without normalization.

On heterophilic graphs such as Cornell and Texas, the behavior is different. PairNorm has a weaker effect on the depth dynamics, and rewiring strategies often improve accuracy compared to the baseline across multiple depths.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/No_pairnorm/cora_0.1_gcn.png" class="img-fluid rounded z-depth-1" alt="Cora GCN accuracy across depth without PairNorm">
  </div>
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/Pairnorm/cora_0.1_gcn.png" class="img-fluid rounded z-depth-1" alt="Cora GCN accuracy across depth with PairNorm">
  </div>
</div>

<div class="caption">
GCN test accuracy across depth on Cora, without PairNorm and with PairNorm.
</div>

<div class="row">
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/No_pairnorm/cornell_0.1_gcn.png" class="img-fluid rounded z-depth-1" alt="Cornell GCN accuracy across depth without PairNorm">
  </div>
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/Pairnorm/cornell_0.1_gcn.png" class="img-fluid rounded z-depth-1" alt="Cornell GCN accuracy across depth with PairNorm">
  </div>
</div>

<div class="caption">
GCN test accuracy across depth on Cornell, without PairNorm and with PairNorm.
</div>

These results show that topology correction and oversmoothing control affect different aspects of depth behavior. Rewiring can improve communication across the graph, while PairNorm helps stabilize representations against collapse.

## Representation-level analysis

Accuracy alone does not tell us whether different rewiring strategies produce similar internal representations. For this reason, we also analyze the learned embeddings.

We use a linear probe on the penultimate-layer embeddings to measure how linearly separable the learned representations are before the final classifier. This helps evaluate whether the intermediate representation remains informative as depth increases.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/linear_probe/no_pairnorm/cora/curv.png" class="img-fluid rounded z-depth-1" alt="Linear probe on Cora with curvature rewiring without PairNorm">
  </div>
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/linear_probe/no_pairnorm/cora/remove_res.png" class="img-fluid rounded z-depth-1" alt="Linear probe on Cora with resistance add-remove rewiring without PairNorm">
  </div>
</div>

<div class="caption">
Linear-probe accuracy on Cora without PairNorm, comparing curvature rewiring and resistance add-remove rewiring.
</div>

<div class="row">
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/linear_probe/pairnorm/cora/curv.png" class="img-fluid rounded z-depth-1" alt="Linear probe on Cora with curvature rewiring and PairNorm">
  </div>
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/linear_probe/pairnorm/cora/remove_res.png" class="img-fluid rounded z-depth-1" alt="Linear probe on Cora with resistance add-remove rewiring and PairNorm">
  </div>
</div>

<div class="caption">
Linear-probe accuracy on Cora with PairNorm, comparing curvature rewiring and resistance add-remove rewiring.
</div>

We also compare representation similarity across rewiring strategies using **Centered Kernel Alignment (CKA)**. This measures whether models trained with different rewired graphs learn similar or different representations.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/cka/no_pairnorm/cora.png" class="img-fluid rounded z-depth-1" alt="CKA similarity on Cora without PairNorm">
  </div>
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/cka/pairnorm/cora.png" class="img-fluid rounded z-depth-1" alt="CKA similarity on Cora with PairNorm">
  </div>
</div>

<div class="caption">
CKA similarity between last-layer GCN representations with curvature rewiring and resistance-based rewiring strategies on Cora.
</div>

The representation-level results show that rewiring strategies can reach similar test accuracies while producing different embedding geometries. This is important because topology edits do not only affect final performance; they also change how information is represented inside the network.

## Edge-set overlap between rewiring strategies

We also compare which edges are added by different rewiring strategies. The UpSet plots show intersections between added-edge sets at budget \(r = 0.1\).

<div class="row">
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/upset/cora.png" class="img-fluid rounded z-depth-1" alt="UpSet plot of added edges on Cora">
  </div>
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/upset/cornell.png" class="img-fluid rounded z-depth-1" alt="UpSet plot of added edges on Cornell">
  </div>
</div>

<div class="caption">
Overlap between edge sets added by different rewiring strategies at budget \(r = 0.1\).
</div>

This graph-level analysis confirms that different rewiring criteria can modify different parts of the graph before training begins.

## Curvature and resistance operate at different scales

Curvature-based rewiring and resistance-based rewiring both aim to address bottlenecks, but they use different signals.

Curvature focuses on local geometric bottlenecks <d-cite key="ToppingEtAl2022"></d-cite>. Effective resistance captures global multi-path connectivity between node pairs <d-cite key="BlackEtAl2023"></d-cite>.

Our experiments show that these methods can sometimes obtain similar accuracy, but the learned representations need not be the same. This suggests that the choice of rewiring criterion matters not only for performance, but also for the internal structure of the learned embeddings.

## Directed graphs

For directed graphs, we use a directed generalization of effective resistance <d-cite key="YoungScardoviLeonard2015"></d-cite>. Since directed effective resistance is only well-defined under appropriate connectivity conditions, we restrict pairwise computations to nodes within the same strongly connected component.

This keeps the resistance computation well-defined, but also restricts which bottlenecks can be modified. The directed extension therefore provides a principled first step toward topology correction in directed message-passing settings.

## Limitations

Effective resistance is informative, but computing it is costly, especially in directed settings. This makes scaling and frequent recomputation a concern.

Another limitation is that resistance is task-agnostic. It improves connectivity according to graph structure, not according to label semantics. In heterophilic graphs, improving connectivity can also increase harmful mixing across classes, especially in deeper models.

These observations suggest that topology correction is most reliable when combined with mechanisms that explicitly control representation mixing.

## Main takeaway

Over-squashing is strongly connected to graph topology. If information has to travel through narrow structural bottlenecks, increasing depth alone may not be enough.

Effective resistance provides a global signal for identifying weak communication pathways. By adding edges between high-resistance node pairs and removing low-resistance edges when connectivity is preserved, ERR modifies the graph in a controlled way.

The experiments show that resistance-guided rewiring can improve connectivity and signal propagation, especially in heterophilic settings. However, the results also show a trade-off: reducing over-squashing can increase mixing and interact with oversmoothing, particularly in deeper models.

The central lesson is that topology-aware GNN design should consider both sides of this trade-off:

> Better connectivity can help long-range communication, but it must be balanced against representation collapse and harmful mixing.

## References

<d-bibliography></d-bibliography>