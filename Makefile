ISO_NAME := Darkly_i386.iso
ISO_URL := https://cdn.intra.42.fr/isos/Darkly_i386.iso

.PHONY: iso

iso: $(ISO_NAME)

$(ISO_NAME):
	curl --fail --location --retry 3 --output "$@.part" "$(ISO_URL)"
	mv "$@.part" "$@"
