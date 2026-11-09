import type { StoredDocument } from "./types";

export const demoDocument: StoredDocument = {
  id: "demo", name: "Voorbeeld — Hypotheekvoorwaarden", size: 0, type: "txt", createdAt: Date.UTC(2026, 9, 20), pageCount: 3,
  blocks: [
    { id: "demo-rente", page: 1, text: "De lening bedraagt € 250.000. De rente bedraagt 3,8% op jaarbasis en staat vast gedurende een rentevaste periode van tien jaar. Na afloop van deze periode wordt een nieuwe rente vastgesteld op basis van de op dat moment geldende tarieven." },
    { id: "demo-aflossing", page: 1, text: "De lening heeft een looptijd van dertig jaar en wordt annuïtair afgelost. De maandelijkse bruto betaling bedraagt gedurende de eerste rentevaste periode ongeveer € 1.165. Het bedrag kan na een renteherziening wijzigen." },
    { id: "demo-extra", page: 2, text: "De kredietnemer kan ieder kalenderjaar maximaal tien procent van de oorspronkelijke hoofdsom boetevrij extra aflossen. Over het meerdere kan een vergoeding wegens vervroegde aflossing verschuldigd zijn, afhankelijk van het financiële nadeel voor de geldverstrekker." },
    { id: "demo-risico", page: 2, text: "Wanneer de kredietnemer niet tijdig aan de betalingsverplichtingen voldoet, kan de geldverstrekker na aanmaning maatregelen treffen. In ernstige gevallen kan dit leiden tot opeisbaarheid van de lening en verkoop van het onderpand." },
    { id: "demo-kosten", page: 3, text: "De kosten van de notaris, taxatie en eventueel hypotheekadvies komen voor rekening van de kredietnemer. Deze kosten zijn niet inbegrepen in het genoemde maandbedrag." },
    { id: "demo-onderpand", page: 3, text: "Als zekerheid voor de lening wordt een recht van hypotheek gevestigd op de woning. Dit houdt in dat de geldverstrekker onder bepaalde wettelijke voorwaarden de woning kan laten verkopen als de schuld niet wordt betaald." },
  ],
  analysis: {
    mode: "demo", limited: false, headline: "Dit moet je weten over je hypotheek", introduction: "Dit fictieve document beschrijft een hypotheek van € 250.000. Hieronder staan de voorwaarden die de meeste invloed hebben op je maandlasten en financiële risico's.",
    sections: [
      { title: "Je lening in het kort", points: [
        { id: "demo-p1", text: "Je leent € 250.000 tegen 3,8% rente. Die rente blijft tien jaar gelijk. Daarna kan de rente hoger of lager worden.", sourceIds: ["demo-rente"] },
        { id: "demo-p2", text: "Je betaalt ongeveer € 1.165 bruto per maand. Na tien jaar kan dit bedrag veranderen.", sourceIds: ["demo-aflossing"] },
      ]},
      { title: "Wat mag je extra aflossen?", points: [
        { id: "demo-p3", text: "Elk jaar mag je tot € 25.000 extra aflossen zonder boete. Bij meer aflossen kan een vergoeding gelden.", sourceIds: ["demo-extra"] },
      ]},
      { title: "Risico's en andere kosten", points: [
        { id: "demo-p4", text: "Als je structureel niet betaalt, kan de bank uiteindelijk verkoop van je woning afdwingen. Daar gaan wettelijke stappen aan vooraf.", sourceIds: ["demo-risico", "demo-onderpand"] },
        { id: "demo-p5", text: "Notaris, taxatie en eventueel hypotheekadvies betaal je apart. Deze kosten zitten niet in je maandbedrag.", sourceIds: ["demo-kosten"] },
      ]},
    ],
    keyTerms: [{ term: "Rentevaste periode", explanation: "De periode waarin je afgesproken rentepercentage niet verandert." }, { term: "Annuïtair aflossen", explanation: "Je betaalt iedere maand een vast bruto bedrag zolang de rente gelijk blijft, verdeeld over rente en aflossing." }],
  },
};
