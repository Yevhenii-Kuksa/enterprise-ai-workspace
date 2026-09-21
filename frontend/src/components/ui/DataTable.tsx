import type { ReactNode } from 'react'

type DataTableColumn<T> = {
  key: string
  header: ReactNode
  render: (row: T) => ReactNode
  width?: string
}

type DataTableProps<T> = {
  columns: DataTableColumn<T>[]
  rows: T[]
  getRowKey: (row: T) => string
  emptyState?: ReactNode
}

function DataTable<T>({
  columns,
  rows,
  getRowKey,
  emptyState,
}: DataTableProps<T>) {
  if (rows.length === 0) {
    return (
      <div className="ui-table-wrapper">
        <div className="ui-empty-state">
          {emptyState ?? 'Brak danych do wyświetlenia.'}
        </div>
      </div>
    )
  }

  return (
    <div className="ui-table-wrapper">
      <table className="ui-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                style={
                  column.width
                    ? { width: column.width }
                    : undefined
                }
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {rows.map((row) => (
            <tr key={getRowKey(row)}>
              {columns.map((column) => (
                <td key={column.key}>
                  {column.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export type {
  DataTableColumn,
  DataTableProps,
}

export default DataTable