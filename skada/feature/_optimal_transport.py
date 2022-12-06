from skorch.utils import to_tensor

from .utils import deepjdot_loss
from .base import BaseDANetwork


class DeepJDOT(BaseDANetwork):
    """Loss DeepJDOT.

    See [1]_.

    Parameters
    ----------
    module : torch module (class or instance)
        A PyTorch :class:`~torch.nn.Module`. In general, the
        uninstantiated class should be passed, although instantiated
        modules will also work.
    criterion : torch criterion (class)
        The uninitialized criterion (loss) used to optimize the
        module.
    layer_names : list of tuples
        The names of the module's layers whose outputs are
        collected during the training.
    reg_d : float, default=1
        Distance term regularization parameter.
    reg_cl : float, default=1
        Class distance term regularization parameter.
    class_weight : array, shape=(n_classes)
        Weight of classes to compute target classes loss.
        If None, don't use weights.
    n_classes : int, default=2
        Number of classes in the data.
    **kwargs : dict
        Keyword arguments passed to the skorch Model class.

    References
    ----------
    .. [1]  Bharath Bhushan Damodaran, Benjamin Kellenberger,
            Remi Flamary, Devis Tuia, and Nicolas Courty.
            DeepJDOT: Deep Joint Distribution Optimal Transport
            for Unsupervised Domain Adaptation. In ECCV 2018
            15th European Conference on Computer Vision,
            September 2018. Springer.
    """

    def __init__(
        self,
        module,
        criterion,
        layer_names,
        reg_d=1,
        reg_cl=1,
        class_weights=None,
        n_classes=2,
        **kwargs
    ):
        super().__init__(
            module, criterion, layer_names, **kwargs
        )
        self.reg_d = reg_d
        self.reg_cl = reg_cl
        self.class_weights = class_weights
        self.n_classes = n_classes

    def _get_loss_da(
        self,
        y_pred,
        y_true,
        embedd,
        embedd_target,
        X=None,
        y_pred_target=None,
        training=True
    ):
        """Compute the domain adaptation loss"""
        y_true = to_tensor(y_true, device=self.device)
        loss_deepjdot = 0
        for i in range(len(embedd)):
            loss_deepjdot += deepjdot_loss(
                embedd[i],
                embedd_target[i],
                y_true,
                y_pred_target,
                self.reg_d,
                self.reg_cl,
                self.class_weights,
                self.n_classes
            )

        loss_classif = self.criterion_(y_pred, y_true)

        return loss_classif + loss_deepjdot, loss_classif, loss_deepjdot
