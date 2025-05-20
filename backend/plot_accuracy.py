import matplotlib.pyplot as plt
import pandas as pd

# Load the training history data
data = pd.read_csv('backend/models/training_history.csv')

# Extract the accuracy and validation accuracy
epochs = range(1, len(data) + 1)
train_accuracy = data['accuracy']
val_accuracy = data['val_accuracy']

# Plot the accuracy graph
plt.figure(figsize=(10, 5))
plt.plot(epochs, train_accuracy, label='Training Accuracy')
plt.plot(epochs, val_accuracy, label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.title('Training and Validation Accuracy')
plt.legend()
plt.grid(True)
plt.savefig('backend/models/accuracy_graph.png')
plt.show()
