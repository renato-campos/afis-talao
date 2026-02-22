USE master;
GO

IF DB_ID(N'AFIS_TALOES') IS NULL
BEGIN
    CREATE DATABASE AFIS_TALOES;
END
GO

USE AFIS_TALOES;
GO

IF OBJECT_ID('dbo.taloes', 'U') IS NULL
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
        CONSTRAINT ck_taloes_status CHECK (status IN ('monitorado', 'finalizado', 'cancelado'))
    );
END
GO

IF OBJECT_ID('dbo.monitoramento', 'U') IS NULL
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
END
GO
