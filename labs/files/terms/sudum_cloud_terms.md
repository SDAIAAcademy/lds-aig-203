# Sudum Cloud Model Service Terms

Version 4.2. Fictional terms written for the SDAIA Academy course LDS-AIG-203. Not the terms of any real provider.

## 1. Definitions

1.1 "Service" means Sudum Cloud's hosted model service, reached through its API, and the models offered through it.
1.2 "Customer Content" means inputs the Customer sends to the Service and outputs the Service returns.
1.3 "Model Version" means a dated model identifier such as `sudum-pro-2`. An "Alias" is an identifier such as `sudum-pro-latest` that points to a Model Version chosen by Sudum Cloud.

## 2. Access

2.1 Sudum Cloud grants the Customer a non-exclusive, non-transferable right to use the Service during the subscription term for the Customer's internal business purposes and for products the Customer offers to its own clients.
2.2 No right to the model weights, parameters or source code is granted.

## 3. Restrictions

3.1 The Customer must not resell, sublicense or provide the Service to third parties as a standalone model service.
3.2 The Customer must not use outputs to develop models that compete with the Service.
3.3 No attribution to Sudum Cloud is required. The Customer must not state or imply that Sudum Cloud endorses its products.

## 4. Acceptable use

4.1 The Customer must not use the Service: (a) for unlawful surveillance; (b) to make decisions that produce legal or similarly significant effects on individuals, such as credit, employment or housing decisions, without meaningful human review; (c) to generate content that impersonates a real person without consent.

## 5. Customer Content

5.1 The Customer owns Customer Content.
5.2 Unless the Customer is on the Enterprise plan with Data Controls switched on, Sudum Cloud may use Customer Content to improve and train the Service.
5.3 Sudum Cloud keeps request logs, including Customer Content, for 30 days for abuse monitoring, on every plan.

## 6. Data location

6.1 Customer Content may be processed in any region where Sudum Cloud or its sub-processors operate.
6.2 Enterprise customers may select a storage region. When capacity in that region is constrained, inference may be routed to another region.

## 7. Model lifecycle

7.1 Sudum Cloud may update the Model Version an Alias points to at any time, without notice.
7.2 Sudum Cloud may deprecate a Model Version. A deprecated Model Version keeps working until its retirement date.
7.3 Sudum Cloud gives at least 21 days' notice of a retirement date, by email to the account administrator.
7.4 After the retirement date, requests to that Model Version fail.

## 8. Suspension and termination

8.1 Either party may terminate for convenience with 30 days' notice.
8.2 Sudum Cloud may suspend the Service immediately for a breach of section 4.

## 9. Data export and deletion

9.1 For 14 days after termination the Customer may export its stored Customer Content in Sudum Cloud's JSONL format.
9.2 Sudum Cloud deletes Customer Content within 30 days after termination, and from backups within 90 days. No certificate of deletion is issued.

## 10. Changes to these terms

10.1 Sudum Cloud may change these terms by posting a new version. Continued use after 15 days means acceptance.

## 11. Sub-processors

11.1 The current list of sub-processors is on Sudum Cloud's website. Sudum Cloud gives 10 days' notice of a new sub-processor.
