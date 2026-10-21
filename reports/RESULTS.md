# Experiment results

| Metric | Result |
| --- | --- |
| Accuracy | 0.5594 |
| Balanced Accuracy | 0.6533 |
| Precision | 0.4124 |
| Recall | 0.9110 |
| F1 | 0.5678 |
| Roc Auc | 0.7762 |
| Average Precision | 0.6509 |
| Brier Score | 0.1678 |

| model | validation_roc_auc | test_roc_auc | test_accuracy | test_precision | test_recall | test_f1 | test_brier_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Majority baseline | 0.5000 | 0.5000 | 0.6823 | 0.0000 | 0.0000 | 0.0000 | 0.3177 |
| Logistic regression | 0.6625 | 0.7466 | 0.7340 | 0.9103 | 0.1802 | 0.3009 | 0.1754 |
| Random forest | 0.6951 | 0.7762 | 0.7338 | 0.9607 | 0.1689 | 0.2873 | 0.1678 |
| Gradient boosting | 0.6691 | 0.7785 | 0.7406 | 0.7758 | 0.2578 | 0.3870 | 0.1661 |

| Partition | rows | cancellation_rate | start | end |
| --- | --- | --- | --- | --- |
| train | 57745 | 0.3583 | 2014-03-18 | 2016-08-30 |
| validation | 8321 | 0.2351 | 2016-09-01 | 2016-12-30 |
| test | 26409 | 0.3177 | 2017-01-01 | 2017-08-31 |