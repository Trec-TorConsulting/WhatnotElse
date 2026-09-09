## ADDED Requirements

### Requirement: Automated Cluster Provisioning and Backup
The infrastructure suite SHALL provide a Kubernetes Job for automated site initialization (`site-init-job.yaml`), a recurring MariaDB backup CronJob (`mariadb-backup-cronjob.yaml`), and PodDisruptionBudgets (`pdb.yaml`).

#### Scenario: Automated site provisioning
- **WHEN** the `whatnot-site-init` job runs
- **THEN** it provisions the Frappe bench site, installs `erpnext` and `whatnot_else`, and exits with code 0.
