# Frappe Project

This is a custom Frappe application designed to extend and enhance functionalities within the Frappe framework.

## 🚀 Getting Started

Follow the steps below to set up and run the project smoothly.

### 1. Get the App

```bash
bench get-app <repo-url>
```

### 2. Install the App on Your Site

Replace `your-site-name` with your actual site name:

```bash
bench --site your-site-name install-app workflowbuild
```

Then restart the bench:

```bash
bench restart
```

## ✅ Required Setup

To ensure smooth operation of the project, complete the following steps:

### 1. Add Worker with Scheduler in `Procfile`

In the **root directory of your Frappe bench**, open or create the `Procfile` and add the following line:

```
rq: rq worker --with-scheduler
```

### 2. Make Sure to add workflow Configuration to make it run

### 3. Add .env File in root folder with below content

```
SITE_PATH=/home/mycomputer/Pankaj/WorkFlow2/frappe-bench/sites
SITE_NAME=workflow.local
DB_NAME=_28ce80########

```

## 💡 Notes

- Ensure `bench start` or `bench start --watch` is running during development.
- Always restart the bench after installation or configuration changes:

```bash
bench restart
```
----------------------------
### For Docker Compose projects

- remember to edit the compose file with the following, so that we could have the custom-queues running and recognized y frappe's `RQ-Worker-list`
- inside `configurator` service in `command` block
```bash
bench set-config -gp workers '{"default": {"timeout": 500}, "long": {"timeout": 500}, "short": {"timeout": 500}, "email": {"timeout": 500}, "sms": {"timeout": 500}, "todo": {"timeout": 500}}'
```