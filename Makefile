SRC_DIR = ./src
PROTO_DIR := $(SRC_DIR)/nexosim/_proto
PROTO_FILE := $(PROTO_DIR)/simulation.proto

.PHONY: proto
proto:
	python -m grpc_tools.protoc -I$(SRC_DIR) --python_out=$(SRC_DIR) --pyi_out=$(SRC_DIR) --grpc_python_out=$(SRC_DIR) $(PROTO_FILE)
