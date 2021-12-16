# Zartan Terraform Scripts By Verticals

Contains all HCL that can be used for the local development.

**NOTE**: You do not need to use Terraform and Okta Provider to provision your Okta tenant. Only for those that are comfortable learning Terraform or practitioner.

## Pre-Requirements

* Terraform v1.+

## Quick Start

Copy vertical name of the `{vertical-name}.tfvars.sample` to `{vertical-name}.tfvars`

```bash
cp admin.tfvars.sample admin.tfvars
```

Update the `tfvars` file with your Okta tenant configuration.

```bash
cat admin.tfvars

# Output
# org_name        = "<okta_subdomain, e.g. atko>"
# api_token       = "<okta_api_token>"
# base_url        = "<the okta domain  e.g. oktapreview.com, okta.com, or okta-emea.com>"
```

Initialize Terraform to pull down Okta Provider.

```bash
terraform init
```

Execute Terraform plan with reference to the `.tfvars` files and plan output file `admin.tfplan`. **NOTE**: `.tfplan` extension can be anything, it just best practices to use `.tfplan`.

```bash
terraform plan -var-file=admin.tfvars -out=admin.tfplan
```

Execute Terraform `apply` with reference to the generated `admin.tfplan` file. The by product should only provision your Okta tenant but also provide you with `.env` file.

```bash
terraform apply admin.tfplan
```

Clean up infrastructure that you just created.

```bash
terraform destroy --lock=false -var-file=admin.tfvars
```

## Resources

Highly recommending using a Terraform Version Manager tool like [tfenv](https://github.com/tfutils/tfenv).
