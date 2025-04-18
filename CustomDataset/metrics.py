import numpy as np
from sklearn.metrics import precision_recall_fscore_support, roc_curve, auc, precision_recall_curve
import matplotlib.pyplot as plt
import seaborn as sns
import os

def calculate_metrics(y_true, y_pred, y_score=None, labels=None):
    """
    Calculate precision, recall, F1-score, and AUC for each class
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        y_score: Predicted probabilities or decision function scores
        labels: List of class labels
        
    Returns:
        Dictionary containing precision, recall, F1-score, and AUC for each class
    """
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, labels=labels)
    
    metrics = {
        'precision': precision,
        'recall': recall,
        'f1': f1
    }
    
    if y_score is not None:
        n_classes = len(np.unique(y_true))
        roc_auc = []
        for i in range(n_classes):
            # Convert to binary classification for each class
            y_true_binary = check_pred(y_true, i)
            if len(np.unique(y_true_binary)) > 1:  # Only calculate if both classes are present
                fpr, tpr, _ = roc_curve(y_true_binary, y_score[:, i])
                roc_auc.append(auc(fpr, tpr))
            else:
                roc_auc.append(0.0)  # If only one class is present, AUC is not defined
        metrics['auc'] = roc_auc
    
    return metrics

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def plot_roc_curve(y_true, y_score, class_names=None, title="ROC Curves", save_dir="plots"):
    """
    Plot ROC curves for each class and save the figure
    
    Args:
        y_true: Ground truth labels
        y_score: Predicted probabilities or decision function scores
        class_names: List of class names
        title: Title of the plot
        save_dir: Directory to save the plot
    """
    ensure_dir(save_dir)
    n_classes = len(np.unique(y_true))
    if class_names is None:
        class_names = [f'Class {i}' for i in range(n_classes)]
    
    plt.figure(figsize=(10, 8))
    
    for i in range(n_classes):
        # Convert to binary classification for each class
        y_true_binary = check_pred(y_true, i)
        if len(np.unique(y_true_binary)) > 1:  # Only plot if both classes are present
            fpr, tpr, _ = roc_curve(y_true_binary, y_score[:, i])
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, label=f'{class_names[i]} (AUC = {roc_auc:.2f})')
    
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title)
    plt.legend(loc="lower right")
    plt.grid(True)
    
    # Save the figure
    plt.savefig(os.path.join(save_dir, 'roc_curves.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_precision_recall_curve(y_true, y_score, class_names=None, title="Precision-Recall Curves", save_dir="plots"):
    """
    Plot Precision-Recall curves for each class and save the figure
    
    Args:
        y_true: Ground truth labels
        y_score: Predicted probabilities or decision function scores
        class_names: List of class names
        title: Title of the plot
        save_dir: Directory to save the plot
    """
    ensure_dir(save_dir)
    n_classes = len(np.unique(y_true))
    if class_names is None:
        class_names = [f'Class {i}' for i in range(n_classes)]
    
    plt.figure(figsize=(10, 8))
    
    for i in range(n_classes):
        # Convert to binary classification for each class
        y_true_binary = check_pred(y_true, i)
        if len(np.unique(y_true_binary)) > 1:  # Only plot if both classes are present
            precision, recall, _ = precision_recall_curve(y_true_binary, y_score[:, i])
            pr_auc = auc(recall, precision)
            plt.plot(recall, precision, label=f'{class_names[i]} (AUC = {pr_auc:.2f})')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(title)
    plt.legend(loc="lower left")
    plt.grid(True)
    
    # Save the figure
    plt.savefig(os.path.join(save_dir, 'precision_recall_curves.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_metrics_bar(metrics, class_names=None, title="Classification Metrics", save_dir="plots"):
    """
    Plot precision, recall, F1-score, and AUC as grouped bar chart and save the figure
    
    Args:
        metrics: Dictionary containing precision, recall, F1-score, and AUC
        class_names: List of class names
        title: Title of the plot
        save_dir: Directory to save the plot
    """
    ensure_dir(save_dir)
    if class_names is None:
        class_names = [f'Class {i}' for i in range(len(metrics['precision']))]
    
    x = np.arange(len(class_names))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - 1.5*width, metrics['precision'], width, label='Precision')
    rects2 = ax.bar(x - 0.5*width, metrics['recall'], width, label='Recall')
    rects3 = ax.bar(x + 0.5*width, metrics['f1'], width, label='F1-Score')
    
    if 'auc' in metrics:
        rects4 = ax.bar(x + 1.5*width, metrics['auc'], width, label='AUC')
    
    ax.set_ylabel('Score')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(class_names)
    ax.legend()
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                       xy=(rect.get_x() + rect.get_width()/2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom')
    
    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    if 'auc' in metrics:
        autolabel(rects4)
    
    fig.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(save_dir, 'classification_metrics.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_metrics_line(metrics_history, title="Metrics Over Time", save_dir="plots"):
    """
    Plot precision, recall, F1-score, and AUC over time as line plot and save the figure
    
    Args:
        metrics_history: List of dictionaries containing metrics for each epoch
        title: Title of the plot
        save_dir: Directory to save the plot
    """
    ensure_dir(save_dir)
    epochs = range(1, len(metrics_history) + 1)
    
    plt.figure(figsize=(12, 6))
    
    # Plot for each class
    n_classes = len(metrics_history[0]['precision'])
    for class_idx in range(n_classes):
        plt.subplot(1, n_classes, class_idx + 1)
        
        precision = [m['precision'][class_idx] for m in metrics_history]
        recall = [m['recall'][class_idx] for m in metrics_history]
        f1 = [m['f1'][class_idx] for m in metrics_history]
        
        plt.plot(epochs, precision, 'b-', label='Precision')
        plt.plot(epochs, recall, 'g-', label='Recall')
        plt.plot(epochs, f1, 'r-', label='F1-Score')
        
        if 'auc' in metrics_history[0]:
            auc_scores = [m['auc'][class_idx] for m in metrics_history]
            plt.plot(epochs, auc_scores, 'y-', label='AUC')
        
        plt.title(f'Class {class_idx}')
        plt.xlabel('Epoch')
        plt.ylabel('Score')
        plt.legend()
        plt.grid(True)
    
    plt.suptitle(title)
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(save_dir, 'metrics_over_time.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_confusion_matrix(y_true, y_pred, class_names=None, title="Confusion Matrix", save_dir="plots"):
    """
    Plot confusion matrix with normalized values and save the figure
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        class_names: List of class names
        title: Title of the plot
        save_dir: Directory to save the plot
    """
    ensure_dir(save_dir)
    from sklearn.metrics import confusion_matrix
    import seaborn as sns
    
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    # Plot normalized confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
                xticklabels=class_names,
                yticklabels=class_names)
    plt.title(title)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig(os.path.join(save_dir, 'confusion_matrix_normalized.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot raw counts confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names,
                yticklabels=class_names)
    plt.title(f"{title} (Raw Counts)")
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig(os.path.join(save_dir, 'confusion_matrix_raw.png'), dpi=300, bbox_inches='tight')
    plt.close() 

def check_pred(y_true, i):
    y = []
    for i in range(len(y_true)):
        if y_true[i] == i:
            y.append(1)
        else:
            y.append(0)
        
    return y