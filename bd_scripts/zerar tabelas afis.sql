use AFIS_TALOES;
BEGIN TRY
    BEGIN TRAN;

    -- Limpa primeiro a tabela filha (FK para taloes)
    DELETE FROM dbo.monitoramento;
    DELETE FROM dbo.taloes;

    -- Reseta os IDs (IDENTITY) para começar novamente em 1
    DBCC CHECKIDENT ('dbo.monitoramento', RESEED, 0);
    DBCC CHECKIDENT ('dbo.taloes', RESEED, 0);

    COMMIT TRAN;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRAN;

    THROW;
END CATCH;
