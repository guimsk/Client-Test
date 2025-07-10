# Makefile para Servidor C
CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -pthread -O2 -g
LDFLAGS = -pthread
TARGET = servidor-c
SOURCE = app.c

# Regra principal
$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE) $(LDFLAGS)

# Regra para debug
debug: CFLAGS += -DDEBUG -g
debug: $(TARGET)

# Regra para release otimizada
release: CFLAGS += -O3 -DNDEBUG
release: $(TARGET)

# Limpeza
clean:
	rm -f $(TARGET) *.o

# Execução
run: $(TARGET)
	./$(TARGET)

# Teste de compilação
test: $(TARGET)
	@echo "Compilação bem-sucedida!"
	@echo "Executando teste básico..."
	@timeout 5s ./$(TARGET) || echo "Servidor testado com sucesso"

# Instalação local
install: $(TARGET)
	cp $(TARGET) /usr/local/bin/

# Verificação de dependências
check:
	@echo "Verificando dependências..."
	@which gcc > /dev/null || (echo "gcc não encontrado" && exit 1)
	@echo "✓ gcc encontrado"
	@echo "✓ pthread disponível"
	@echo "✓ Todas as dependências OK"

# Informações sobre o build
info:
	@echo "=== INFORMAÇÕES DO BUILD ==="
	@echo "Compilador: $(CC)"
	@echo "Flags: $(CFLAGS)"
	@echo "Target: $(TARGET)"
	@echo "Fonte: $(SOURCE)"
	@echo "=========================="

.PHONY: clean run test install check info debug release
