import pandas as pd

def cobertura(doc, cobertura_df, df_fato):
    # Initial setup
    stk_i = max(df_fato['projecao'].iloc[0] if not df_fato.empty else 0, 0)
    stk = stk_i
    invoi = doc.loc[doc['status_documento'] == 'INVOI', 'quantidade_convertida'].sum()
    po = doc.loc[doc['status_documento'] == 'PO', 'quantidade_convertida'].sum()
    op = doc.loc[doc['status_documento'] == 'OP', 'quantidade_convertida'].sum()

    frc = 0
    nivel_stk = []
    label = []

    # Loop over demands
    for demanda in cobertura_df['quantidade_demanda']:
        if stk > 0:
            stk -= demanda
            nivel_stk.append(stk)
            label.append('STK')
        elif invoi > 0:
            invoi -= demanda
            nivel_stk.append(invoi)
            label.append('INVOI')
        elif po > 0:
            po -= demanda
            nivel_stk.append(po)
            label.append('PO')
        elif op >0:
          op-= demanda
          nivel_stk.append(op)
          label.append('OP')
        else:
            frc -= demanda
            nivel_stk.append(frc)
            label.append('DEMAND')

    # Create base DataFrame
    cobertura_df = cobertura_df.copy()
    cobertura_df['estoque'] = nivel_stk
    cobertura_df['status'] = label

    # Convert dates to datetime
    cobertura_df['data'] = pd.to_datetime(cobertura_df['data'], format='%d-%m-%Y', errors='coerce')

    # Valor inicial
    nova_linha = {
        'data': cobertura_df['data'].iloc[0] - pd.Timedelta(weeks=1),
        'quantidade_demanda': 0.0,
        'estoque': stk_i,
        'status': cobertura_df['status'].iloc[0]
    }

    # Concatenate
    cobertura_df = pd.concat([pd.DataFrame([nova_linha]), cobertura_df], ignore_index=True)

    # Interpolação
    start_date = cobertura_df['data'].min()
    end_date = cobertura_df['data'].max()
    start_date = start_date - pd.Timedelta(days=start_date.weekday())
    date_range = pd.date_range(start=start_date, end=end_date, freq='W-MON')
    template_df = pd.DataFrame({'data': date_range})
    merged_df = pd.merge(template_df, cobertura_df, on='data', how='left')
    merged_df['quantidade_demanda'] = merged_df['quantidade_demanda'].fillna(0)
    merged_df['estoque'] = merged_df['estoque'].ffill()
    merged_df['status'] = merged_df['status'].ffill()
    merged_df['data'] = merged_df['data'].dt.strftime('%d-%m-%Y')

    return merged_df.reset_index(drop=True)