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
  <strong>Venue:</strong> Accepted as a poster at the GRaM Workshop @ ICLR 2026<br>
  <strong>Authors:</strong> Bertran Miquel-Oliver, Manel Gil-Sorribes, Victor Guallar, Alexis Molina<br>
  <strong>arXiv:</strong> <a href="https://arxiv.org/abs/2603.11944" target="_blank">2603.11944</a>
</div>

<div style="margin-bottom: 1.5em;"></div>

Graph Neural Networks (GNNs) update node representations by aggregating information from neighboring nodes. This message-passing mechanism gives GNNs a strong inductive bias for relational data, but it also constrains how information can propagate through a graph <d-cite key="KipfWelling2017GCN"></d-cite>.

When useful information is far away, a GNN needs multiple layers to propagate it. However, increasing depth does not automatically solve long-range reasoning. If many distant nodes can influence a target node only through a narrow set of intermediate nodes or edges, their information has to be compressed into fixed-size vectors. This can strongly attenuate long-range signals.
This phenomenon is known as **over-squashing** <d-cite key="AlonYahav2020"></d-cite>.

In our GRaM workshop paper at ICLR 2026, **Effective Resistance Rewiring: A Simple Topological Correction for Over-Squashing**, we study over-squashing as a topology-driven limitation measuring through **effective resistance** and propose a graph rewiring strategy based on this signal. The method adds edges between high-resistance node pairs and removes low-resistance edges when connectivity is preserved. This controlled rewiring improves weak communication pathways while avoiding unnecessary densification.

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

$$
R_{ij} = (e_i - e_j)^T L^\dagger (e_i - e_j)
$$

where $L^\dagger$ is the Moore-Penrose pseudoinverse of the graph Laplacian.

Large values of $R_{ij}$ indicate weak multi-path connectivity, which is consistent with bottlenecked information transmission. Effective resistance has also been connected to over-squashing through bounds on message-passing influence <d-cite key="BlackEtAl2023"></d-cite>.

In the directed setting, we use a directed notion of effective resistance <d-cite key="YoungScardoviLeonard2015"></d-cite>. Since directed graphs do not have symmetric reachability, we restrict resistance computations to node pairs within the same strongly connected component. This lets us apply the same bottleneck-based intuition while respecting the directionality of the graph.

## Effective Resistance Rewiring

We propose **Effective Resistance Rewiring (ERR)**, a controlled add-remove rewiring strategy.

At each rewiring step:

1. Find the node pair with the largest effective resistance.
2. Add an edge to improve this weak communication pathway.
3. When remove edge operations are allowed
   3.1. Find an edge with very small effective resistance.
   3.2. Remove that edge only if connectivity is preserved.

The goal is to strengthen poorly connected regions, while avoiding uncontrolled graph densification.

The method is parameter-free beyond the rewiring budget. The budget controls the number of allowed edge edits. This allows us to study the trade-off between improving connectivity and controlling mixing. This process is computed once before training, so it does not add overhead to the training loop.

## Experimental setting

We evaluate the method on node classification datasets with different graph regimes:

- **Homophilic graphs:** Cora and CiteSeer
- **Heterophilic graphs:** Cornell and Texas

We study GCNs on undirected settings and DirGCN in directed settings <d-cite key="TongEtAl2020DirGCN"></d-cite>. We also compare models with and without **PairNorm**, a normalization method designed to mitigate oversmoothing <d-cite key="ZhaoAkoglu2019PairNorm"></d-cite>.

The experiments analyze:

- test accuracy as depth increases,
- the interaction between rewiring and PairNorm,
- study the similarity of learned representations across rewiring strategies using multiple metrics, including:
  - linear-probe accuracy on penultimate-layer embeddings <d-cite key="alain2016understanding"></d-cite>,
  - cosine similarity between same-class and different-class node embeddings,
  - CKA similarity between representations learned under different rewiring strategies <d-cite key="kornblith2019similarity"></d-cite>.

Datasets and splits are loaded through PyTorch Geometric <d-cite key="fey2019fast"></d-cite>, while hyperparameters are taken from previous works <d-cite key="ZhaoAkoglu2019PairNorm"></d-cite><d-cite key="TongEtAl2020DirGCN"></d-cite>.

## Accuracy across depth

The first set of results studies GCN test accuracy as the number of layers increases.

On homophilic citation graphs, accuracy tends to degrade with depth when PairNorm is not used. This is consistent with oversmoothing in deeper models. PairNorm stabilizes the depth trend and reduces the sharp degradation observed without normalization.

On heterophilic graphs, the behavior is different. PairNorm has a weaker effect on the depth dynamics, and rewiring strategies often improve accuracy compared to the baseline across multiple depths.

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

## How rewiring changes learned representations

Accuracy alone does not tell us whether different rewiring strategies produce similar internal representations. Two rewired graphs may reach comparable test accuracy while inducing different message-passing trajectories and different embedding geometries.

This motivates the following question:

> Do different rewiring strategies lead to similar or different learned representations?

To study this, we first compare learned representations using **Centered Kernel Alignment (CKA)** <d-cite key="kornblith2019similarity"></d-cite>. CKA measures similarity between representations while being invariant to orthogonal transformations and isotropic scaling, making it useful for comparing independently trained models.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/cka/no_pairnorm/cora.png" class="img-fluid rounded z-depth-1" alt="CKA similarity on Cora without PairNorm">
  </div>
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/cka/pairnorm/cora.png" class="img-fluid rounded z-depth-1" alt="CKA similarity on Cora with PairNorm">
  </div>
</div>

<div class="caption">
CKA similarity between last-layer GCN representations with curvature rewiring and resistance-based rewiring strategies on Cora. When CKA is close to 1, the two representations are very similar. When CKA is close to 0, the two representations are very different.
</div>

The CKA analysis shows that different rewiring strategies can produce different learned representations, even when their final accuracies are similar. This suggests that the rewiring criterion affects not only performance, but also the geometry of the learned embedding space.

One reason is that each rewiring strategy changes the graph in a different way before training. Curvature-based rewiring and resistance-based rewiring are both motivated by bottlenecks, but they operate at different structural scales. Curvature focuses on local geometric bottlenecks <d-cite key="ToppingEtAl2022"></d-cite>, while effective resistance captures global multi-path connectivity between node pairs <d-cite key="BlackEtAl2023"></d-cite>.

To check whether different rewiring criteria actually modify different parts of the graph, we compare the sets of edges added by each method. The UpSet plots show intersections between added-edge sets at budget \(r = 0.1\).

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

These plots support that different rewiring criteria are generating different initial graph topologies, which can lead to different message-passing trajectories and different embedding geometries after training.

After observing that different rewiring strategies can lead to different representations, we next ask whether these representations remain useful for classification.

We use a linear probe on the penultimate-layer embeddings to measure how linearly separable the learned representations are before the final classifier <d-cite key="alain2016understanding"></d-cite>. This provides a complementary view to CKA: while CKA compares representation similarity across methods, the linear probe evaluates how informative those representations are for the downstream task.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/linear_probe/no_pairnorm/cora/curv.png" class="img-fluid rounded z-depth-1" alt="Linear probe on Cora with curvature rewiring without PairNorm">
  </div>
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/linear_probe/no_pairnorm/cora/remove_res.png" class="img-fluid rounded z-depth-1" alt="Linear probe on Cora with resistance add-remove rewiring without PairNorm">
  </div>
</div>

<div class="caption">
Linear-probe accuracy on Cora without PairNorm, comparing curvature rewiring (left) and resistance add-remove rewiring (right).
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
Linear-probe accuracy on Cora with PairNorm, comparing curvature rewiring (left) and resistance add-remove rewiring (right).
</div>

The linear-probe results helps to understand that PairNorm stabilizes the depth trend of probe accuracy, while resistance-driven rewiring changes the depth at which informative embeddings appear. In the unnormalized setting, resistance-based rewiring also reduces part of the degradation observed as depth increases. This supports the interpretation that normalization and topology correction act on complementary aspects of the problem: PairNorm controls oversmoothing, while resistance-based rewiring modifies the graph bottlenecks that constrain information flow.

Finally, we analyze cosine similarity between node embeddings from the same class and from different classes. This tracks how message passing changes the relation between class structure and embedding geometry across layers.

This diagnostic is useful for interpreting the interaction between rewiring, depth, and PairNorm: rewiring can improve communication across the graph, but repeated aggregation may also increase mixing between classes.

<div class="row">
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/cosine/no_pairnorm/cora/none.png" class="img-fluid rounded z-depth-1" alt="Cosine similarity on Cora baseline without PairNorm">
  </div>
  <div class="col-sm mt-3 mt-md-0">
    <img src="/posts/effective-resistance-rewiring/images/cosine/no_pairnorm/cora/remove_res.png" class="img-fluid rounded z-depth-1" alt="Cosine similarity on Cora with resistance add-remove rewiring without PairNorm">
  </div>
</div>

<div class="caption">
Mean cosine similarity between node embeddings from the same class and different classes on Cora without PairNorm.
</div>

Together, CKA, edge-set overlap, linear probing, and cosine similarity show that rewiring should not be interpreted only through final accuracy. Different topology corrections can modify different parts of the graph, produce different embedding geometries, and affect how class information is preserved across layers.

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

Refer yourself to the <a href="https://arxiv.org/abs/2603.11944" target="_blank">paper</a> for more details on the method, experiments, and analysis.

## References

<d-bibliography></d-bibliography>
