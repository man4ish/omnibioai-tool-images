export type ToolStatus = 'built' | 'reused' | 'license' | 'missing'

export interface Tool {
  name: string
  category: string
  sif_path: string | null
  sif_filename: string
  sif_exists: boolean
  sif_size_mb: number | null
  status: ToolStatus
  dockerfile: string
  updated_at: string | null
}
