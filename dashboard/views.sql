CREATE VIEW dashboard_documents AS
SELECT DISTINCT t.name AS tenant, i.name AS interview, d.created_date as document_created, d.status as document_status, ii.name as document_type
FROM tenant_tenant AS t
INNER JOIN document_document AS d
ON t.id = d.tenant_id
INNER JOIN interview_interview AS i
ON d.interview_id = i.id
INNER JOIN interview_interviewdocumenttype ii on i.document_type_id = ii.id
WHERE t.name NOT IN ('Educa Legal', 'Development', 'Autotest', 'NETO')
AND  i.name NOT IN ('Autotest_Acordo Individual de Trabalho - Redução de Jornada/Redução Salarial MP 936-2020',
                    'Autotest_Termo de Uso e Responsabilidade - Iscool App',
                    'Autotest_Termo de Acordo - Mudança do Regime de Jornada e Cessão do Direito Autoral',
                    'Autotest_Proposta de Renegociação - Fluxo de Pagamento',
                    'Autotest_Proposta de Renegociação - Desconto no Valor Devido',
                    'Autotest_Proposta de Renegociação - Contrato de Locação',
                    'Autotest_Termo de Acordo Individual para Banco de Horas MP 927-2020',
                    'Autotest_Contrato de comodato de imóvel',
                    'Autotest_Contrato de viagem de formação pedagógica',
                    'Autotest_Aditivo ao contrato de trabalho - banco de horas',
                    'Autotest_Contrato de diretor estatutário',
                    'Autotest_Contrato de cessão de espaço',
                    'Autotest_Termo de confissão de dívida',
                    'Autotest_Notificação de cobrança',
                    'Autotest_Contrato de locação de imóvel',
                    'Autotest_Contrato de prestação de serviços',
                    'Autotest_Autorização de uso de imagem',
                    'Autotest_Contrato de consultoria',
                    'Autotest_Contrato do aluno',
                    'Autotest_Termo de confidencialidade - NDA',
                    'Autotest_Autorização de uso de imagem');

GRANT ALL PRIVILEGES ON dashboard_documents to "educa-legal-app";

CREATE VIEW dashboard_tenants AS
SELECT DISTINCT t.name AS tenant, t.created_date, t.auto_enrolled, p.name
FROM tenant_tenant AS t
INNER JOIN billing_plan AS p
ON t.plan_id = p.id
WHERE t.name NOT IN ('Educa Legal', 'Development', 'Autotest', 'NETO');

GRANT ALL PRIVILEGES ON dashboard_tenants to "educa-legal-app";

CREATE VIEW dashboard_schools AS
SELECT DISTINCT t.name AS tenant, ss.name
FROM tenant_tenant AS t
INNER JOIN school_school ss on t.id = ss.tenant_id
WHERE t.name NOT IN ('Educa Legal', 'Development', 'Autotest', 'NETO');

GRANT ALL PRIVILEGES ON dashboard_schools to "educa-legal-app";
