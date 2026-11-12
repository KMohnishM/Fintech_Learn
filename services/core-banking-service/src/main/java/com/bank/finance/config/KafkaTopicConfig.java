package com.bank.finance.config;

import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;

@Configuration
public class KafkaTopicConfig {

    @Bean
    public NewTopic lcIssuedTopic() {
        return TopicBuilder.name("trade.lc.issued")
                .partitions(3)
                .replicas(1)
                .build();
    }

    @Bean
    public NewTopic docsUploadedTopic() {
        return TopicBuilder.name("trade.docs.uploaded")
                .partitions(3)
                .replicas(1)
                .build();
    }

    @Bean
    public NewTopic verificationCompletedTopic() {
        return TopicBuilder.name("trade.verification.completed")
                .partitions(3)
                .replicas(1)
                .build();
    }

    @Bean
    public NewTopic paymentSettledTopic() {
        return TopicBuilder.name("trade.payment.settled")
                .partitions(3)
                .replicas(1)
                .build();
    }
}
