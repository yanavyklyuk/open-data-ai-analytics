variable "resource_group_name" {
  default = "rg-nuclear-security-lab-4"
}

variable "location" {
  default = "West Europe"
}

variable "vm_name" {
  default = "nuclear-security-vm"
}

variable "ssh_public_key_path" {
  default = "/home/azureuser/.ssh/id_rsa.pub"
}