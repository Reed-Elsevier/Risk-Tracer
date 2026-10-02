import InvestigationView from "@/components/InvestigationView";

export default async function InvestigationPage({
  params
}: {
  params: Promise<{ invoiceId: string }>;
}) {
  const { invoiceId } = await params;
  return <InvestigationView invoiceId={invoiceId} />;
}
