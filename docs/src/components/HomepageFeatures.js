import React from 'react';
import clsx from 'clsx';
import styles from './HomepageFeatures.module.css';


const FeatureList = [
  {
    title: 'Question Answering',
    Svg: require('../../static/img/question-answering.svg').default,
    description: (
      <>
          Explore the existing models and datasets to answer more specific research questions using integrated
          interpretability tools.
      </>
    ),
  },
  {
    title: 'Analyze QA Skills',
    Svg: require('../../static/img/analysis.svg').default,
    description: (
      <>
          Study the strengths and weaknesses of existing models by comparing them on a wide range of tasks and
          datasets that are already provided within our framework.
      </>
    ),
  },
  {
    title: 'Create Your Own',
    Svg: require('../../static/img/dev-code.svg').default,
    description: (
      <>
        Create your own custom QA skills to analyze different models and datastores.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
  // <div >
  //     <img src={require('../../static/img/square-arch.png').default} align={'left'}/>
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} alt={title} />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p align="left">{description}</p>
    </div>
  </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
