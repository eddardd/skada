"""
Optimal Transport Domain Adaptation (OTDA)
==========================================

This example illustrates the OTDA method from [1] on a simple classification task.

.. [1] N. Courty, R. Flamary, D. Tuia and A. Rakotomamonjy,
        Optimal Transport for Domain Adaptation, in IEEE
        Transactions on Pattern Analysis and Machine Intelligence

"""

# Author: Remi Flamary
#
# License: MIT License
# sphinx_gallery_thumbnail_number = 4

# %%
import matplotlib.pyplot as plt

from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.svm import SVC

from skada.datasets import make_shifted_datasets
from skada import (OTmapping, EntropicOTmapping, ClassRegularizerOTmapping,
                   LinearOTmapping)


# %%
# Generate concept drift dataset
# ------------------------------
n_samples = 20
X_source, y_source, X_target, y_target = make_shifted_datasets(
        n_samples_source=n_samples,
        n_samples_target=n_samples+1,
        shift='concept_drift',
        noise=0.1,
        random_state=42,
)
n_tot_source = X_source.shape[0]
n_tot_target = X_target.shape[0]

plt.figure(1, figsize=(8, 3.5))
plt.subplot(121)

plt.scatter(X_source[:, 0], X_source[:, 1], c=y_source, vmax=9, cmap='tab10', alpha=0.7)
plt.title("Source domain")
lims = plt.axis()

plt.subplot(122)
plt.scatter(X_target[:, 0], X_target[:, 1], c=y_target, vmax=9, cmap='tab10', alpha=0.7)
plt.title("Target domain")
plt.axis(lims)

# %%
# Illustration of the DA problem
# ------------------------------

# Train on source

clf = SVC(kernel='rbf', C=1)
clf.fit(X_source, y_source)

# Compute acuracy on source and target
ACC_source = clf.score(X_source, y_source)
ACC_target = clf.score(X_target, y_target)

plt.figure(2, figsize=(8, 3.5))
plt.subplot(121)
DecisionBoundaryDisplay.from_estimator(
    clf, X_source, alpha=0.3, eps=0.5, response_method="predict", vmax=9,
    cmap='tab10', ax=plt.gca())
plt.scatter(X_source[:, 0], X_source[:, 1], c=y_source, vmax=9, cmap='tab10', alpha=0.7)
plt.title("SVC Prediction on source (ACC={:.2f})".format(ACC_source))
lims = plt.axis()

plt.subplot(122)
DecisionBoundaryDisplay.from_estimator(
    clf, X_source, alpha=0.3, eps=0.5, response_method="predict", vmax=9,
    cmap='tab10', ax=plt.gca())
plt.scatter(X_target[:, 0], X_target[:, 1], c=y_target, vmax=9, cmap='tab10', alpha=0.7)
plt.title("SVC Prediction on target (ACC={:.2f})".format(ACC_target))
lims = plt.axis()

# %%
# Optimal Transport Domain Adaptation
# -----------------------------------

clf_otda = OTmapping(base_estimator=SVC(kernel='rbf', C=1))
clf_otda.fit(X_source, y_source, X_target=X_target)

# Compute acuracy on source and target
ACC_source = clf_otda.score(X_source, y_source)
ACC_target = clf_otda.score(X_target, y_target)

plt.figure(3, figsize=(8, 3.5))
plt.subplot(121)
DecisionBoundaryDisplay.from_estimator(
    clf_otda, X_source, alpha=0.3, eps=0.5, response_method="predict", vmax=9,
    cmap='tab10', ax=plt.gca())
plt.scatter(X_source[:, 0], X_source[:, 1], c=y_source, vmax=9, cmap='tab10', alpha=0.7)
plt.title("OTDA Prediction on source (ACC={:.2f})".format(ACC_source))
lims = plt.axis()

plt.subplot(122)
DecisionBoundaryDisplay.from_estimator(
    clf_otda, X_source, alpha=0.3, eps=0.5, response_method="predict", vmax=9,
    cmap='tab10', ax=plt.gca())
plt.scatter(X_target[:, 0], X_target[:, 1], c=y_target, vmax=9, cmap='tab10', alpha=0.7)
plt.title("OTDA Prediction on target (ACC={:.2f})".format(ACC_target))
lims = plt.axis()

# %%
# How does OTDA works?
# --------------------
#
# The OTDA method is based on the following idea: the optimal transport between
# the source and target feature distribution is computed (which gives us what is
# called an optimal plan). Then, the source samples are mapped to the target
# distribution using this optimal plan and the classifier is trained on the
# mapped  # samples.
#
# We illustrate below the different steps of the OTDA method.

# recovering the OT plan
T = clf_otda.ot_transport_.coupling_
T = T / T.max()

# computing the transported samples
X_source_adapted = clf_otda.predict_adapt(X_source, y_source, X_target)[0]

plt.figure(4, figsize=(12, 3.5))
plt.subplot(131)
for i in range(n_tot_source):
    for j in range(n_tot_target):
        if T[i, j] > 0:
            plt.plot([X_source[i, 0], X_target[j, 0]],
                     [X_source[i, 1], X_target[j, 1]], '-g', alpha=T[i, j])
plt.scatter(X_source[:, 0], X_source[:, 1], c=y_source, vmax=9, cmap='tab10', alpha=0.7)
plt.scatter(X_target[:, 0], X_target[:, 1], c='C7', alpha=0.7)
plt.title(label="Step 1: compute OT plan")
lims = plt.axis()

plt.subplot(132)
plt.scatter(X_target[:, 0], X_target[:, 1], c='C7', alpha=0.7)
plt.scatter(X_source_adapted[:, 0], X_source_adapted[:, 1],
            c=y_source, vmax=9, cmap='tab10', alpha=0.7)
plt.axis(lims)
plt.title(label="Step 2: adapt source distribution")

plt.subplot(133)
DecisionBoundaryDisplay.from_estimator(
    clf_otda, X_source, alpha=0.3, eps=0.5, response_method="predict", vmax=9,
    cmap='tab10', ax=plt.gca())
plt.scatter(X_target[:, 0], X_target[:, 1], c='C7', alpha=0.7)
plt.scatter(X_source_adapted[:, 0], X_source_adapted[:, 1],
            c=y_source, vmax=9, cmap='tab10', alpha=0.7)
plt.axis(lims)
plt.title(label="Step 3: train on adapted source")

# %%
# Different OTDA methods
# ----------------------
#
# The OTDA method can be used with different optimal transport solvers. Here we
# illustrate the different methods available in SKADA.

# Sinkhorn OT solver
clf_otda_sinkhorn = EntropicOTmapping(base_estimator=SVC(kernel='rbf', C=1), reg_e=1)
clf_otda_sinkhorn.fit(X_source, y_source, X_target=X_target)
ACC_sinkhorn = clf_otda_sinkhorn.score(X_target, y_target)
X_source_adapted_sinkhorn = clf_otda_sinkhorn.predict_adapt(
    X_source, y_source, X_target)[0]

# Sinkhorn OT solver with class regularization
clf_otds_classreg = ClassRegularizerOTmapping(
    base_estimator=SVC(kernel='rbf', C=1), reg_e=0.2, reg_cl=1)
clf_otds_classreg.fit(X_source, y_source, X_target=X_target)
ACC_classreg = clf_otds_classreg.score(X_target, y_target)
X_source_adapted_classreg = clf_otds_classreg.predict_adapt(
    X_source, y_source, X_target)[0]

# Linear OT solver
clf_otda_linear = LinearOTmapping(base_estimator=SVC(kernel='rbf', C=1))
clf_otda_linear.fit(X_source, y_source, X_target=X_target)
ACC_linear = clf_otda_linear.score(X_target, y_target)
X_source_adapted_linear = clf_otda_linear.predict_adapt(X_source, y_source, X_target)[0]

plt.figure(5, figsize=(14, 7))

plt.subplot(241)
plt.scatter(X_target[:, 0], X_target[:, 1], c='C7', alpha=0.7)
plt.scatter(X_source_adapted[:, 0], X_source_adapted[:, 1],
            c=y_source, vmax=9, cmap='tab10', alpha=0.7)
plt.axis(lims)
plt.title(label="OTDA adapted")

plt.subplot(242)
plt.scatter(X_target[:, 0], X_target[:, 1], c='C7', alpha=0.7)
plt.scatter(X_source_adapted_sinkhorn[:, 0], X_source_adapted_sinkhorn[:, 1],
            c=y_source, vmax=9, cmap='tab10', alpha=0.7)
plt.axis(lims)
plt.title(label="OTDA Sinkhorn adapted")

plt.subplot(243)
plt.scatter(X_target[:, 0], X_target[:, 1], c='C7', alpha=0.7)
plt.scatter(X_source_adapted_classreg[:, 0], X_source_adapted_classreg[:, 1],
            c=y_source, vmax=9, cmap='tab10', alpha=0.7)
plt.axis(lims)
plt.title(label="OTDA class reg adapted")

plt.subplot(244)
plt.scatter(X_target[:, 0], X_target[:, 1], c='C7', alpha=0.7)
plt.scatter(X_source_adapted_linear[:, 0], X_source_adapted_linear[:, 1],
            c=y_source, vmax=9, cmap='tab10', alpha=0.7)
plt.axis(lims)
plt.title(label="OTDA linear adapted")

plt.subplot(245)
DecisionBoundaryDisplay.from_estimator(
    clf_otda, X_source, alpha=0.3, eps=0.5, response_method="predict", vmax=9,
    cmap='tab10', ax=plt.gca())
plt.scatter(X_target[:, 0], X_target[:, 1], c=y_target, vmax=9, cmap='tab10', alpha=0.7)
plt.axis(lims)
plt.title(label="OTDA (ACC={:.2f})".format(ACC_target))

plt.subplot(246)
DecisionBoundaryDisplay.from_estimator(
    clf_otda_sinkhorn, X_source, alpha=0.3, eps=0.5, response_method="predict", vmax=9,
    cmap='tab10', ax=plt.gca())
plt.scatter(X_target[:, 0], X_target[:, 1], c=y_target, vmax=9, cmap='tab10', alpha=0.7)
plt.axis(lims)
plt.title(label="OTDA Sinkhorn (ACC={:.2f})".format(ACC_sinkhorn))

plt.subplot(247)
DecisionBoundaryDisplay.from_estimator(
    clf_otds_classreg, X_source, alpha=0.3, eps=0.5, response_method="predict", vmax=9,
    cmap='tab10', ax=plt.gca())
plt.scatter(X_target[:, 0], X_target[:, 1], c=y_target, vmax=9, cmap='tab10', alpha=0.7)
plt.axis(lims)
plt.title(label="OTDA class reg (ACC={:.2f})".format(ACC_classreg))

plt.subplot(248)
DecisionBoundaryDisplay.from_estimator(
    clf_otda_linear, X_source, alpha=0.3, eps=0.5, response_method="predict", vmax=9,
    cmap='tab10', ax=plt.gca())
plt.scatter(X_target[:, 0], X_target[:, 1], c=y_target, vmax=9, cmap='tab10', alpha=0.7)
plt.axis(lims)
plt.title(label="OTDA linear (ACC={:.2f})".format(ACC_linear))
