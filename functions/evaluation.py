from sklearn.metrics import precision_score, recall_score

def evaluate_predictions(y_true, y_pred):
    """
    Calculates precision and recall for the predicted instrument channels.
    
    Parameters:
        y_true (array-like): True labels.
        y_pred (array-like): Predicted labels.
    
    Returns:
        tuple: Precision and recall scores.
    """
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    return precision, recall