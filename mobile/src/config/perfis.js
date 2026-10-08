// Perfis de saúde suportados pelo backend, com descrição para o usuário.
// Os perfis sensíveis (asmático, idoso, criança) recebem alertas mais cedo.

export const PERFIS = [
  {
    valor: "geral",
    rotulo: "Geral",
    icone: "person-outline",
    descricao:
      "Sem condições de saúde específicas. Recebe alertas quando o ar fica Ruim ou pior.",
  },
  {
    valor: "asmatico",
    rotulo: "Asmático",
    icone: "medkit-outline",
    descricao:
      "Tem asma, rinite ou outra doença respiratória. Recebe alertas já com o ar Moderado.",
  },
  {
    valor: "idoso",
    rotulo: "Idoso",
    icone: "accessibility-outline",
    descricao:
      "Tem 60 anos ou mais e é mais sensível à poluição. Recebe alertas já com o ar Moderado.",
  },
  {
    valor: "atleta",
    rotulo: "Atleta",
    icone: "walk-outline",
    descricao:
      "Pratica exercícios ao ar livre. As recomendações focam em quando e onde treinar.",
  },
  {
    valor: "crianca",
    rotulo: "Criança",
    icone: "happy-outline",
    descricao:
      "Para crianças, que respiram mais ar em proporção ao corpo. Alertas já com o ar Moderado.",
  },
];

export function rotuloDoPerfil(valor) {
  return PERFIS.find((p) => p.valor === valor)?.rotulo || valor || "--";
}
