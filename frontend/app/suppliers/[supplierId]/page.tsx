import SupplierView from "@/components/SupplierView";

export default async function SupplierPage({ params }: { params: Promise<{ supplierId: string }> }) {
  const { supplierId } = await params;
  return <SupplierView supplierId={supplierId} />;
}
