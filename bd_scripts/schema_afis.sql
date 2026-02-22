-- ====================================================================
-- SCRIPT: Criação condicional de banco (AFIS_TALOES ou AUDITA_AFIS)
-- Autor: DBA Experiente
-- ====================================================================

SET NOCOUNT ON;

DECLARE @CriouAfis BIT = 0;
DECLARE @BancoDestino NVARCHAR(128);

-- =============================================
-- 1. Verifica existência de AFIS_TALOES
-- =============================================
IF DB_ID(N'AFIS_TALOES') IS NULL
BEGIN
    BEGIN TRY
        CREATE DATABASE AFIS_TALOES;
        PRINT '✅ Banco AFIS_TALOES criado com sucesso.';
        SET @CriouAfis = 1;
    END TRY
    BEGIN CATCH
        PRINT '❌ Erro ao criar AFIS_TALOES: ' + ERROR_MESSAGE();
        THROW;
    END CATCH
END
ELSE
BEGIN
    PRINT 'ℹ️ AFIS_TALOES já existe.';
    
    IF DB_ID(N'AUDITA_AFIS') IS NULL
    BEGIN
        BEGIN TRY
            CREATE DATABASE AUDITA_AFIS;
            PRINT '✅ Banco AUDITA_AFIS criado com sucesso.';
        END TRY
        BEGIN CATCH
            PRINT '❌ Erro ao criar AUDITA_AFIS: ' + ERROR_MESSAGE();
            THROW;
        END CATCH
    END
    ELSE
    BEGIN
        PRINT 'ℹ️ AUDITA_AFIS já existe.';
    END
    
    SET @CriouAfis = 0;
END

-- =============================================
-- 2. Define qual banco será usado
-- =============================================
IF @CriouAfis = 1
    SET @BancoDestino = N'AFIS_TALOES';
ELSE
    SET @BancoDestino = N'AUDITA_AFIS';

-- =============================================
-- 3. Cria as tabelas no banco de destino (via execução dinâmica)
-- =============================================
DECLARE @sql NVARCHAR(MAX) = '
USE ' + QUOTENAME(@BancoDestino) + ';

PRINT ''▼ Banco atual: '' + DB_NAME();

-- Criação da tabela taloes
IF OBJECT_ID(''dbo.taloes'', ''U'') IS NULL
BEGIN
    CREATE TABLE dbo.taloes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        ano INT NOT NULL,
        talao INT NOT NULL,
        data_solic DATE NOT NULL,
        hora_solic TIME(0) NOT NULL,
        delegacia NVARCHAR(255) NOT NULL,
        autoridade NVARCHAR(255) NOT NULL,
        solicitante NVARCHAR(255) NOT NULL,
        endereco NVARCHAR(500) NOT NULL,
        boletim NVARCHAR(100) NULL,
        natureza NVARCHAR(255) NULL,
        data_bo DATE NULL,
        vitimas NVARCHAR(500) NULL,
        equipe NVARCHAR(255) NULL,
        operador NVARCHAR(100) NOT NULL,
        status NVARCHAR(20) NOT NULL,
        observacao NVARCHAR(MAX) NULL,
        criado_em DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        atualizado_em DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT uq_taloes_ano_talao UNIQUE (ano, talao),
        CONSTRAINT ck_taloes_status CHECK (status IN (''monitorado'', ''finalizado'', ''cancelado''))
    );
    PRINT ''✅ Tabela taloes criada em ' + @BancoDestino + ''';
END
ELSE
BEGIN
    PRINT ''ℹ️ Tabela taloes já existe em ' + @BancoDestino + ''';
END

-- Criação da tabela monitoramento
IF OBJECT_ID(''dbo.monitoramento'', ''U'') IS NULL
BEGIN
    CREATE TABLE dbo.monitoramento (
        id INT IDENTITY(1,1) PRIMARY KEY,
        talao_id INT NOT NULL UNIQUE,
        proximo_alerta DATETIME2 NOT NULL,
        intervalo_min INT NOT NULL DEFAULT 30,
        criado_em DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT fk_monitoramento_talao
            FOREIGN KEY (talao_id) REFERENCES dbo.taloes(id) ON DELETE CASCADE
    );
    PRINT ''✅ Tabela monitoramento criada em ' + @BancoDestino + ''';
END
ELSE
BEGIN
    PRINT ''ℹ️ Tabela monitoramento já existe em ' + @BancoDestino + ''';
END
';

EXEC sp_executesql @sql;

PRINT '🚀 Processo concluído. Banco em uso: ' + @BancoDestino;
GO