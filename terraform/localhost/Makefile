
.ONESHELL:
.SHELL := /usr/bin/bash
.DEFAULT_GOAL := help

ROOT_PATH := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/../..)
ZARTAN_VERTICALS := admin credit dealer developer ecommerce finance healthcare healthcare-oie hospitality streamingservice travelagency
ZARTAN_TF_TARGET := admin

REQUIRED_TOOLS := terraform jq
$(foreach bin,$(REQUIRED_TOOLS),\
    $(if $(shell command -v $(bin) 2> /dev/null),$(info Found `$(bin)`),$(error Please install `$(bin)`)))

.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: clean-tfstate
clean-tfstate: validate-tfstate ## Remove terraform assoicated files. ie. *.tfstate, *.tfplan, etc.
	@echo "+ $@"
	@find ${PWD} -type f -name '*.tfstate*' -exec rm -f {} +
	@find ${PWD} -type f -name '*.tfplan*' -exec rm -f {} +
	@find ${PWD} -type f -name '*.terraform.lock.hcl*' -exec rm -f {} +

.PHONY: clean-all
clean-all: clean-tfstate ## Remove .terraform local cache directory. Really start fresh!
	@echo "+ $@"
	@find ${PWD} -type d -name '.terraform' -exec rm -rf {} +

.PHONY: validate
validate: format ## Validate HCL script files.
	@echo "+ $@"
	@echo "Looping through verticals: "
	for veriticals in ${ZARTAN_VERTICALS}; do \
		pushd $$veriticals; \
		echo "### Start ###"; \
		echo "#Validating: ${PWD}"; \
		TF_IN_AUTOMATION=1 terraform init -backend=false && terraform validate || exit 1; \
		echo "### End ###"; \
		popd; \
	done

.PHONY: format
format: ## Format HCL script files.
	@echo "+ $@"
	TF_IN_AUTOMATION=1 terraform fmt -recursive

.PHONY: apply
apply: clean-tfstate ## Apply single vertical. default: ZARTAN_TF_TARGET=admin. !WARNING: Creates a tfstate file!
	@echo "+ $@"
	pushd ${ZARTAN_TF_TARGET} || exit 1; \
	TF_IN_AUTOMATION=1 terraform -version; \
	TF_IN_AUTOMATION=1 terraform init; \
	TF_IN_AUTOMATION=1 terraform plan -var-file=${ZARTAN_TF_TARGET}.tfvars -out=${ZARTAN_TF_TARGET}.tfplan; \
	TF_IN_AUTOMATION=1 terraform apply -auto-approve "${ZARTAN_TF_TARGET}.tfplan"; \
	TF_IN_AUTOMATION=1 terraform destroy -var-file=${ZARTAN_TF_TARGET}.tfvars -auto-approve; \
	popd; \

.PHONY: test
test: clean-tfstate validate ## Run complete terraform init & plan subcommand on all the veriticals.
	@echo "+ $@"
	@echo "Start running through all veriticals: "
	for veriticals in ${ZARTAN_VERTICALS}; do \
		pushd $$veriticals; \
		terraform -version; \
		echo "### Start ###"; \
		echo "#Testing: ${PWD}"; \
		TF_IN_AUTOMATION=1 terraform init; \
		TF_IN_AUTOMATION=1 terraform plan -var-file=$$veriticals.tfvars -out=$$veriticals.tfplan; \
		echo "### End ###"; \
		popd; \
	done

.PHONY: validate-tfstate
validate-tfstate: ## Validate the terraform.tfstate file exist and can be 'apply' can be performed.
	@echo "+ $@"
	for veriticals in ${ZARTAN_VERTICALS}; do \
		pushd $$veriticals; \
		if [ -f "${PWD}/$$veriticals/terraform.tfstate" ]; then \
			cat ${PWD}/$$veriticals/terraform.tfstate | jq -e '.resources | length == 0' || exit 1; \
		fi; \
		popd; \
	done
