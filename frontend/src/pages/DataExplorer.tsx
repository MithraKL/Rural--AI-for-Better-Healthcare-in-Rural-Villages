import { useRef, useState } from "react";
import { useApi } from "@/lib/useApi";
import { api } from "@/lib/api";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatNumber } from "@/lib/format";
import type { UploadResponse } from "@/types";

const SOURCES = ["RHS", "HMIS", "NFHS", "DLHS", "AHS", "Anganwadi"];

export default function DataExplorer() {
  const [refreshKey, setRefreshKey] = useState(0);
  const datasets = useApi(() => api.datasets(), [refreshKey]);
  const [source, setSource] = useState("RHS");
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [recomputing, setRecomputing] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  async function handleUpload() {
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadResult(null);
    try {
      const res = await api.uploadDataset(source, file);
      setUploadResult(res);
      setRefreshKey((k) => k + 1);
    } catch (e) {
      setUploadResult({ success: false, message: e instanceof Error ? e.message : String(e), dataset: null, errors: [] });
    } finally {
      setUploading(false);
    }
  }

  async function handleRecompute() {
    setRecomputing(true);
    try {
      await api.recompute();
      setRefreshKey((k) => k + 1);
    } finally {
      setRecomputing(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-ink-900">Data Explorer</h1>
        <p className="text-sm text-ink-500">
          Every dataset powering RuralCare AI, its geographic granularity, and a real ingestion pipeline for uploading
          RHS / HMIS / NFHS / DLHS / AHS / Anganwadi files (CSV, Excel or JSON).
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Ingested Datasets" />
          <CardBody className="overflow-x-auto p-0">
            <table className="w-full text-sm">
              <thead className="bg-ink-50 text-xs uppercase text-ink-500">
                <tr>
                  <th className="px-4 py-2 text-left">Source</th>
                  <th className="px-4 py-2 text-left">Granularity</th>
                  <th className="px-4 py-2 text-right">Rows</th>
                  <th className="px-4 py-2 text-left">Type</th>
                  <th className="px-4 py-2 text-left">Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {datasets.data?.map((d) => (
                  <tr key={d.id} className="border-t border-ink-100">
                    <td className="px-4 py-2 font-medium">{d.source_name}</td>
                    <td className="px-4 py-2 capitalize text-ink-600">{d.granularity}</td>
                    <td className="px-4 py-2 text-right">{formatNumber(d.row_count)}</td>
                    <td className="px-4 py-2">{d.is_demo ? <Badge tone="warn">Demo</Badge> : <Badge tone="brand">Real</Badge>}</td>
                    <td className="px-4 py-2 text-xs text-ink-500">{new Date(d.uploaded_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Upload New Dataset" />
          <CardBody className="space-y-3">
            <select className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" value={source} onChange={(e) => setSource(e.target.value)}>
              {SOURCES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
            <input ref={fileRef} type="file" accept=".csv,.xlsx,.xls,.json" className="w-full text-xs" />
            <button onClick={handleUpload} disabled={uploading} className="w-full rounded-lg bg-brand-600 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50">
              {uploading ? "Uploading…" : "Upload"}
            </button>
            {uploadResult && (
              <div className={`rounded-lg p-3 text-xs ${uploadResult.success ? "bg-emerald-50 text-emerald-800" : "bg-red-50 text-red-700"}`}>
                <p>{uploadResult.message}</p>
                {uploadResult.errors.map((e, i) => <p key={i} className="mt-1">⚠ {e}</p>)}
              </div>
            )}
            <hr className="border-ink-100" />
            <button onClick={handleRecompute} disabled={recomputing} className="w-full rounded-lg border border-ink-300 py-2 text-sm font-semibold text-ink-700 hover:bg-ink-50 disabled:opacity-50">
              {recomputing ? "Recomputing pipeline…" : "Recompute AI pipeline with latest data"}
            </button>
            <p className="text-[11px] text-ink-400">
              Rows referencing a village/district not already in the geography database are rejected, never fabricated.
              Village/HMIS/Anganwadi data must be village-level; NFHS/DLHS/AHS are district-level only.
            </p>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
